import pandas as pd
import numpy as np
import xarray as xr
import boto3
import io
import geopandas as gpd
import shapely.geometry
import os
from pathlib import Path


class DataLoader:
    """A class for managing and loading data resources for the TNC web application.

    Data Attributes:
    ----------
        gdf_outline : geopandas.GeoDataFrame
            Geospatial outline of the region.
        gdf : geopandas.GeoDataFrame
            Hydrofabric data for catchment divides.
        gdf_wells : geopandas.GeoDataFrame
            Hydrofabric data for wells.
        gdf_lines : geopandas.GeoDataFrame
            Hydrofabric data for flow paths.
        df_nf : pandas.DataFrame
            Weighted natural flows dataset.
        df_cabcm : dict
            Dictionary of California Basin Characterization Model (CABCM) datasets.
        tnc_domain_q : pandas.DataFrame
            Basin comparison dataset with monthly flow volumes.
        df_q : pandas.DataFrame
            Simulated monthly volume from NGen.
        ds_ngen : xarray.Dataset
            NGen validation data formatted for dashboard use.
        gw_delta : dict
            Monthly groundwater delta data.
        cfe_routed_flow_af : pd.DataFrame
            Routed monthly flows from CFE (groundwater cal.)
        cfe_routed_flow_af : pd.DataFrame
            Routed monthly flows from CFE (groundwater cal.)
    """

    def __init__(
        self,
        bucket_name: str = None,
        s3_resource: bool = None,
        ngen_output_dir: str = None,
        local_data_dir: str = None,
    ):
        """Load all datasets necessary to run the webapp.

        Typical runtime should be 3-5 seconds, depending on network speed.

        Parameters:
        ----------
        bucket_name : str
            Name of the S3 bucket to access.
        s3_resource : boto3.resource
            AWS S3 resource object for accessing bucket data. Defaults to None.
        data_dir : str
            Local directory path for loading static datasets. Defaults to "./data/".
        ngen_output_dir : str
            Path to NGen simulation outputs. Defaults to None.
        """
        self.bucket_name = bucket_name
        # self.data_dir = data_dir
        self.ngen_output_dir = ngen_output_dir
        self.local_data_dir = local_data_dir
        if local_data_dir is not None:
            self.use_local = True
        else:
            self.use_local = False

        if s3_resource is None:
            self.s3_resource = boto3.resource(
                "s3",
                aws_access_key_id=os.getenv("aws_access_key_id"),
                aws_secret_access_key=os.getenv("aws_secret_access_key"),
            )
        else:
            self.s3_resource = s3_resource

        self.s3_client = self.s3_resource.meta.client

        # Load all webapp datasets during initialization
        self.gdf_outline = self.get_outline()
        self.gdf = self.get_hydrofabric(layer="divides")
        self.gdf_wells = self.get_hydrofabric(layer="wells")
        self.gdf_lines = self.get_hydrofabric(layer="flowpaths")

        self.df_nf = self.natural_flows()
        self.df_cabcm = self.get_s3_cabcm()
        self.terraclim = self.get_s3_terraclim()
        self.tnc_domain_q = self.read_tnc_domain_q()
        self.cfe_q = self.cfe_basin_q()
        self.well_data = self.get_s3_well_level()
        self.cfe_routed_flow_af = self.load_cfe_routed_flow_vol()
        self.cfe_routed_flow_cfs = self.load_cfe_routed_flow_rate()

        self.ds_ngen = self.ngen_dashboard_data(
            key="webapp_resources/ngen_validation_20250922_monthly.nc"
        )

        # data processing and aggregation
        self.precip_stats()
        self.ngen_vol_stats()
        self.ngen_stats()

    def pd_read_s3_parquet(self, key, **args):
        """S3 or local"""
        if self.use_local:
            return pd.read_parquet(
                os.path.join(self.local_data_dir, key), **args
            )
        else:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return pd.read_parquet(io.BytesIO(obj["Body"].read()), **args)

    def pd_read_s3_csv(self, key, **args):
        """S3 or local"""
        if self.use_local:
            return pd.read_csv(os.path.join(self.local_data_dir, key), **args)
        else:
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            return pd.read_csv(io.BytesIO(obj["Body"].read()), **args)

    def gpd_read_s3_gpk(self, layer, key, driver="GPKG"):
        """S3 or local"""
        if self.use_local:
            return gpd.read_file(
                os.path.join(self.local_data_dir, key), layer=layer
            )
        else:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=key
            )
            data = response["Body"].read()
            with io.BytesIO(data) as src:
                gdf = gpd.read_file(src, layer=layer)
            return gdf

    def gpd_read_s3_geojson(self, key):
        """S3 or local"""
        if self.use_local:
            return gpd.read_file(os.path.join(self.local_data_dir, key))
        else:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=key
            )
            data = response["Body"].read()
            with io.BytesIO(data) as src:
                gdf = gpd.read_file(src)
            return gdf

    def get_s3_well_level(self) -> pd.DataFrame:
        """
        Load well data (raw)
        """
        df = self.pd_read_s3_parquet(
            key="webapp_resources/gw_level_raw_hourly_feet.parquet"
        )
        return df

    def get_s3_cabcm(self) -> dict[pd.DataFrame]:
        """
        Load California Basin Characterization Model summarization from S3.
        This is the historic water balance (BCM component).

        Frequency: Month

        UNITS:
        AET - mm/month

        Returns:
            dict: Dictionary of pd.DataFrame for each variable.
        """
        model_vars = [
            "aet",
            "cwd",
            "pck",
            "pet",
            "rch",
            "run",
            "str",
            "tmn",
            "tmx",
        ]
        all_vars = {}

        for var in model_vars:
            df = self.pd_read_s3_parquet(
                key=f"water_balance/v2/cabcm/{var}.parquet",
            )
            df.index = pd.to_datetime(df["date"])
            all_vars[var] = df

        return all_vars

    def get_s3_terraclim(self) -> pd.DataFrame:
        """
        Load Terraclim. This is the historic water balance (Terraclim component).

        Frequency: Monthly

        UNITS:

        Returns:
            pd.DataFrame
        """
        model_vars = [
            "aet",
            "def",
            "PDSI",
            "pet",
            "ppt",
            "q",
            "soil",
            "srad",
            "swe",
            "tmax",
            "tmin",
            "vap",
            "vpd",
            "ws",
        ]

        all_vars = {}

        for var in model_vars:
            df = self.pd_read_s3_parquet(
                key=f"water_balance/v2/terraclim/{var}.parquet",
            )
            df.index = pd.to_datetime(df["date"])
            df.drop(columns={"date"}, inplace=True)
            all_vars[var] = df

        return all_vars

    def get_hydrofabric(self, layer: str) -> gpd.GeoDataFrame:
        """
        read hydrofabric from s3 bucket

        Args:
            layer (str): Layer name in the geopackage.

        Returns:
            GeoDataFrame: Geopandas dataframe of the specified layer.
        """
        gdf = self.gpd_read_s3_gpk(
            key="hydrofabric/jldp_ngen_nhdhr_wells.gpkg", layer=layer
        )
        gdf = gdf.to_crs("EPSG:4326")

        if layer == "divides":
            gdf["feature_id"] = gdf["divide_id"].str[4:].astype(int)
            gdf["catchment"] = gdf["divide_id"]  # for joining with NGen data

        elif layer == "wells":
            gdf["lon"] = gdf.geometry.x  # extract longitude
            gdf["lat"] = gdf.geometry.y  # extract latitude

        return gdf

    def cfe_basin_q(self) -> pd.DataFrame:
        """
        Load CFE Q from NGen simulation (and gauge observations).

        Returns:
            DataFrame: Simulated monthly volume in acre-feet
        """
        df = self.pd_read_s3_parquet(
            key="webapp_resources/cfe_20241103_troute_cat23.parquet"
        )  # UNIT: VOL m^3
        df["flow"] *= 0.000810714  # UNIT: m^3 to acre-feet
        df = df.loc["1982-10-01":]
        df["water_year"] = df.index.map(self.water_year)
        return df[["flow", "water_year"]]

    def ngen_csv_to_df(
        self,
        path: str = None,
    ) -> tuple[list[pd.DataFrame], list[str]]:
        """
        Loads NGen CSV outputs.

        Args:
            path (str, optional): Location of NGen output with catchment .csv files.

        Returns:
            tuple: List of DataFrames and list of catchment names.
        """
        if path is None:
            path = self.ngen_output_dir
        cat_paths = list(Path(path).glob("cat-*.csv"))
        catchments = [p.stem for p in cat_paths]
        df_lst = [
            pd.read_csv(p, index_col=["Time"], parse_dates=["Time"])
            for p in cat_paths
        ]

        return df_lst, catchments

    def ngen_csv_to_xr(
        self,
        path: str = None,
        cats_out: bool = False,
    ) -> xr.Dataset | tuple[xr.Dataset, list]:
        """
        Parses NGen model outputs into an xarray Dataset.

        Frequency: Month

        UNITS:
        AET - meters / month

        Args:
            path (str, optional): Path to NGen output CSV files.
            cats_out (bool, optional): If True, returns catchment names along with Dataset.

        Returns:
            Dataset or tuple: xarray Dataset (and catchment names if cats_out is True).
        """
        df_lst, cats = self.ngen_csv_to_df(path)

        data_vars = {}

        # Loop through each DataFrame and each variable (column) to create DataArrays
        for df, catchment in zip(df_lst, cats):
            for column in df.columns:
                if column not in data_vars:
                    data_vars[column] = []
                data_vars[column].append(
                    xr.DataArray(
                        df[column].values,
                        dims=["Time"],
                        coords={"Time": df.index},
                    )
                )

        # Concatenate each variable's DataArrays along the 'catchment' dimension
        for var in data_vars:
            data_vars[var] = xr.concat(
                data_vars[var], dim=pd.Index(cats, name="catchment")
            )

        ds = xr.Dataset(data_vars)

        if cats_out:
            return ds, cats

        return ds

    def ngen_dashboard_data(self, key: str) -> xr.Dataset:
        """
        Pulls NetCDF from S3 or local as an xarray Dataset, formatted for the web app.
        """
        if self.use_local:
            file_path = os.path.join(self.local_data_dir, key)
            ds = xr.open_dataset(file_path, engine="netcdf4")
        else:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name, Key=key
            )
            file_stream = io.BytesIO(response["Body"].read())
            ds = xr.open_dataset(file_stream, engine="h5netcdf")

        ds = ds.sel(Time=slice("1982-10-01", None))
        ds["wy"] = ds["Time"].to_pandas().index.map(self.water_year)

        ds = ds.rename(
            {
                "rain_rate": "RAIN_RATE",
                "direct_runoff": "DIRECT_RUNOFF",
                "infiltration_excess": "INFILTRATION_EXCESS",
                "nash_lateral_runoff": "NASH_LATERAL_RUNOFF",
                "deep_gw_to_channel_flux": "DEEP_GW_TO_CHANNEL_FLUX",
                "soil_to_gw_flux": "SOIL_TO_GW_FLUX",
                "q_out": "Q_OUT",
                "soil_storage": "SOIL_STORAGE",
                "PET": "POTENTIAL_ET",
                "AET": "ACTUAL_ET",
            }
        )

        return ds

    def monthly_gw_delta(self, prefix: str) -> dict[str, pd.DataFrame]:
        """
        Reads a directory of Parquet files from S3 into a dictionary of DataFrames.

        Args:
            prefix (str): Directory (prefix) path within the bucket where the Parquet files are located.

        Returns:
            dict: Dictionary where keys are station IDs and values are DataFrames.
        """
        bucket = self.s3_resource.Bucket(self.bucket_name)
        parquet_dfs = {}

        for obj in bucket.objects.filter(Prefix=prefix):
            key = obj.key
            # print(key)
            if key.endswith(".parquet"):
                obj_body = obj.get()["Body"].read()
                parquet_buffer = io.BytesIO(obj_body)
                df = pd.read_parquet(parquet_buffer)
                stn_id = df["stn_id_dendra"].iloc[0]
                parquet_dfs[stn_id] = df

        return parquet_dfs

    def natural_flows(self) -> pd.DataFrame:
        """
        Loads natural flows data from S3.

        Returns:
            DataFrame: Resampled DataFrame with weighted TNC flow.
        """
        df = self.pd_read_s3_parquet(
            key="water_balance/tnc/weighted_natural_flows.parquet",
        )

        df.index = pd.to_datetime(df["date"])
        df["divide_id"] = df["divide_id"].astype(int)
        df["weighted_tnc_flow"] = (
            df["weighted_tnc_flow"] * 0.0283
        )  # UNIT  # Convert cfs to m³/day

        # Group by 'divide_id' and resample to monthly (resulting in m³ per month)
        resampled_df = (
            df.groupby("divide_id")
            .resample("MS")
            .agg({"weighted_tnc_flow": "sum"})
            .reset_index()
        )
        resampled_df.index = pd.to_datetime(resampled_df.date)
        return resampled_df[["weighted_tnc_flow", "divide_id"]]

    def load_cfe_routed_flow_vol(self):
        """
        Routed flows, monthly volume, in acre-feet
        """
        df = self.pd_read_s3_parquet(
            "webapp_resources/cfe_routed_flow_monthly_af.parquet"
        )
        df = df.loc["1982-10-01":]
        df.columns.name = None

        return df

    def load_cfe_routed_flow_rate(self):
        """
        Routed flows, as a rate in CFS.
        """
        df = self.pd_read_s3_parquet(
            "webapp_resources/cfe_routed_flow_monthly_cfs.parquet"
        )
        df = df.loc["1982-10-01":]
        df.columns.name = None

        return df

    def read_tnc_domain_q(self) -> pd.DataFrame:
        """
        Loads temporary full basin comparison data from S3.

        Returns:
            DataFrame: Monthly volume in acre-feet.
        """
        df = self.pd_read_s3_csv(
            key="webapp_resources/flow_17593507_mean_estimated_1982_2023.csv",
        )

        df["monthly_vol_af"] = (
            df["value"] * 60.369
        )  # UNIT: rate in CFS to vol in acre-feet
        df["date"] = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
        )
        df.reset_index(inplace=True)
        df.index = df["date"]
        df = df[["monthly_vol_af"]]
        return df

    @staticmethod
    def water_year(date: pd.DatetimeTZDtype):
        """
        Convert date to WY
        """
        return date.year if date.month < 10 else date.year + 1

    def get_outline(self) -> gpd.GeoDataFrame:
        """
        reads the outline data from the s3 bucket

        Returns:
            GeoDataFrame: geopandas dataframe with the outline
        """
        gdf = self.gpd_read_s3_geojson(key="location_data/tnc.geojson")
        gdf["ID"] = "dangermond preserve"
        return gdf

    def precip_stats(self):
        """
        Parse historic water balance, or CFE results, to generate
        key summary statistics for use in the dashboard, including
        the text descriptions.

        This should return data for all years, year-specific logic
        should go in `home.update_summary_text()`.

        UNIT: precip -> inches
        """
        # Access precipitation data
        df = self.terraclim["ppt"].copy()
        df["value"] = df["value"] * 0.0393701  # UNIT: mm to inch
        # mean of cats for each timestep
        cat_mean = df.groupby(df.index)[["value"]].mean()
        # assign water year to subset df, which is monthly
        cat_mean["water_year"] = cat_mean.index.map(self.water_year)

        # # Create a new column for water year
        # df["water_year"] = df.index.map(self.water_year)

        # # Group by water year and calculate annual precipitation totals
        # domain_vals = df.groupby("water_year")["value"].mean()

        # sum months to get annual data for each water year
        self.terraclim_ann_precip = cat_mean.groupby("water_year")[
            "value"
        ].sum()
        self.terraclim_ann_precip = self.terraclim_ann_precip.loc["1982":]

        # Compute quartiles for precipitation accumulation
        ppt_quartile = pd.qcut(
            self.terraclim_ann_precip,
            q=5,
            labels=[
                "a far below average",
                "a below average",
                "a near average",
                "an above average",
                "a far above average",
            ],
        )

        # Attach quartiles as a DataFrame with precipitation values for reference
        self.terraclim_ann_precip = pd.DataFrame(
            {
                "wy_precip_inch": self.terraclim_ann_precip,
                "Quartile": ppt_quartile,
            }
        )

        self.terraclim_mean_annual_precip = self.terraclim_ann_precip[
            "wy_precip_inch"
        ].mean()

    def ngen_stats(self):
        """
        process and aggregate ngen simulation for visualizations
        """
        self.ds_ngen["NET_GW_CHANGE_METER"] = (
            self.ds_ngen["SOIL_TO_GW_FLUX"]
            - self.ds_ngen["DEEP_GW_TO_CHANNEL_FLUX"]
        )

        self.ds_ngen["NET_GW_CHANGE_FEET"] = (
            self.ds_ngen["NET_GW_CHANGE_METER"] * 3.28084
        )  # UNIT: meters to feet

        self.ds_ngen["RAIN_RATE_INCH"] = (
            self.ds_ngen["RAIN_RATE"] * 39.3701
        )  # UNIT: meter to inch

        self.ds_ngen["POTENTIAL_ET_INCH"] = (
            self.ds_ngen["POTENTIAL_ET"] * 39.3701
        )  # UNIT: meter to inch

        self.ds_ngen["ACTUAL_ET_INCH"] = (
            self.ds_ngen["ACTUAL_ET"] * 39.3701
        )  # UNIT: meter to inch

        # self.cfe_gw_change_monthly_feet = self.ds_ngen["NET_GW_CHANGE_FEET"].to_pandas()
        # self.cfe_gw_change_monthly_feet["water_year"] = (
        #     self.cfe_gw_change_monthly_feet.index.map(self.water_year)
        # )

        self.ds_ngen["RAIN_RATE_INCHES"] = (
            self.ds_ngen["RAIN_RATE"] * 39.3701
        )  # UNIT: meters to inches

        # ----- ET WY Categories -----------------------
        # monthly to WY
        et_wy_vol_m3 = (
            self.ngen_basinwide_et_loss_m3.groupby("water_year").sum()
        )["ACTUAL_ET_VOL_M3"]

        self.et_wy_quartile = pd.qcut(
            et_wy_vol_m3,
            q=5,
            labels=[
                "far below average",
                "below average",
                "near average",
                "above average",
                "far above average",
            ],
        )

        # ----- Jalama Cr Tributary Stats -----------
        # get flows for Jalama Ck tributaries -----------
        self.jalama_tributaries_monthly_cfs = self.cfe_routed_flow_cfs[
            [42, 58, 36]
        ].copy()
        self.jalama_tributaries_monthly_cfs["water_year"] = (
            self.jalama_tributaries_monthly_cfs.index.map(self.water_year)
        )

    # def get_historic(self):
    #     """
    #     Calculate stats for entire water balance period
    #     """
    #     self.ds_ngen
    #     # df = pd.DataFrame()

    #     # df["DEEP_GW_TO_CHANNEL"] = (
    #     #     self.ds_ngen["DEEP_GW_TO_CHANNEL_FLUX"].mean("catchment").to_pandas()
    #     # )
    #     # df["SOIL_TO_GW_FLUX"] = (
    #     #     self.ds_ngen["SOIL_TO_GW_FLUX"].mean("catchment").to_pandas()
    #     # )
    #     # df["SOIL_STORAGE"] = self.ds_ngen["SOIL_STORAGE"].mean("catchment").to_pandas()

    #     # df["net"] = df["SOIL_TO_GW_FLUX"] - df["DEEP_GW_TO_CHANNEL"]

    #     # df *= 3.2808  # UNIT meters to feet

    #     # self.gw_net = df
    #     # self.gw_delta_yr = df.resample("YE").sum()

    def ngen_vol_stats(self):
        """Calculate storage based on groundwater infiltration and outflow to channel"""
        # Get the list of catchments present in the dataset
        # Conversion factor from cubic feet to acre-feet
        # Conversion factor from km² to ft²
        SQKM_TO_SQFT = 1e6 * 10.7639
        FT3_TO_ACRE_FT = 1 / 43560

        dataset_catchments = self.ds_ngen["catchment"].values

        #  only catchments that exist in the dataset
        catchment_areas = (
            self.gdf.set_index("divide_id")
            .loc[dataset_catchments, "areasqkm"]
            .dropna()  # Drop any missing values to avoid mismatches
        )
        catchment_areas.index.name = "catchment"
        # Convert to an xarray DataArray with matching coordinates
        catchment_areas_xr = xr.DataArray(
            catchment_areas,
            coords={"catchment": catchment_areas.index},
            dims="catchment",
        )
        self.ds_ngen["areasqkm"] = catchment_areas_xr

        self.ds_ngen["area_sqft"] = self.ds_ngen["areasqkm"] * SQKM_TO_SQFT

        # compute total volume (ft³/month) for each catchment
        self.ds_ngen["SOIL_TO_GW_VOL"] = (
            self.ds_ngen["SOIL_TO_GW_FLUX"] * self.ds_ngen["area_sqft"]
        )
        self.ds_ngen["DEEP_GW_TO_CHANNEL_VOL"] = (
            self.ds_ngen["DEEP_GW_TO_CHANNEL_FLUX"] * self.ds_ngen["area_sqft"]
        )

        self.ds_ngen["NET_VOL"] = (
            self.ds_ngen["SOIL_TO_GW_VOL"]
            - self.ds_ngen["DEEP_GW_TO_CHANNEL_VOL"]
        )

        # NET_VOL to acre-feet
        self.ds_ngen["NET_VOL_ACRE_FT"] = (
            self.ds_ngen["NET_VOL"] * FT3_TO_ACRE_FT
        )

        self.ngen_basinwide_gw_storage = (
            self.ds_ngen["NET_VOL_ACRE_FT"]
            .sum(dim="catchment")
            .cumsum()
            .to_pandas()
        )

        # ---------------------------------
        # calculate inflow (precip volume)
        # ds_ngen has been resampled to monthly, using "sum"
        self.ds_ngen["PRECIP_VOL_M3"] = self.ds_ngen["RAIN_RATE"] * (
            self.ds_ngen["areasqkm"] * 1000000
        )  # UNIT: sq_km to sq_m

        self.ngen_basinwide_input_m3 = (
            self.ds_ngen["PRECIP_VOL_M3"].sum(dim="catchment").to_pandas()
        )

        # ---------------------------------
        # calculate ET loss
        self.ds_ngen["ACTUAL_ET_VOL_M3"] = self.ds_ngen["ACTUAL_ET"] * (
            self.ds_ngen["areasqkm"] * 1000000
        )  # UNIT: sq_km to sq_m

        # self.ngen_basinwide_et_loss_m3 = pd.DataFrame(
        #     self.ds_ngen["ACTUAL_ET_VOL_M3"].sum(dim="catchment").to_pandas()
        # )
        self.ngen_basinwide_et_loss_m3 = pd.DataFrame(
            self.ds_ngen["ACTUAL_ET_VOL_M3"].sum(dim="catchment").to_pandas(),
            columns=["ACTUAL_ET_VOL_M3"],
        )

        self.ngen_basinwide_et_loss_m3["water_year"] = (
            self.ngen_basinwide_et_loss_m3.index.map(self.water_year)
        )
