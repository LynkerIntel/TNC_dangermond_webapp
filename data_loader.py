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
    """

    def __init__(
        self,
        bucket_name: str,
        s3_resource: bool = None,
        data_dir: str = "./data/",
        ngen_output_dir: str = None,
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
        self.data_dir = data_dir
        self.ngen_output_dir = ngen_output_dir

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
        self.gdf = self.get_local_hydrofabric(layer="divides")
        self.gdf_wells = self.get_local_hydrofabric(layer="wells")
        self.gdf_lines = self.get_local_hydrofabric(layer="flowpaths")
        self.df_nf = self.natural_flows()
        self.df_cabcm = self.get_s3_cabcm()
        self.terraclim = self.get_s3_terraclim()
        self.tnc_domain_q = self.read_tnc_domain_q()
        self.cfe_q = self.cfe_basin_q()

        self.ds_ngen = self.ngen_dashboard_data(
            key="webapp_resources/ngen_validation_20241103_monthly.nc"
        )
        self.gw_delta = self.monthly_gw_delta(
            prefix="webapp_resources/monthly_gw_delta/"
        )

        # post-processing
        self.precip_stats()
        self.ngen_stats()
        self.ngen_gw_vol()

    def pd_read_s3_parquet(self, key, **args):
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        return pd.read_parquet(io.BytesIO(obj["Body"].read()), **args)

    def pd_read_s3_csv(self, key, **args):
        obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        return pd.read_csv(io.BytesIO(obj["Body"].read()), **args)

    def gpd_read_s3_gpk(self, key, driver="GPKG", **args):
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        data = response["Body"].read()
        with io.BytesIO(data) as src:
            gdf = gpd.read_file(src, driver=driver)
        return gdf

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
        model_vars = ["aet", "cwd", "pck", "pet", "rch", "run", "str", "tmn", "tmx"]
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

    def get_local_hydrofabric(self, layer: str) -> gpd.GeoDataFrame:
        """
        Read from data directory.

        Args:
            layer (str): Layer name in the geopackage.

        Returns:
            GeoDataFrame: Geopandas dataframe of the specified layer.
        """
        filepath = os.path.join(self.data_dir, "jldp_ngen_nhdhr.gpkg")
        gdf = gpd.read_file(filepath, layer=layer)
        gdf = gdf.to_crs("EPSG:4326")

        if layer == "divides":
            gdf["feature_id"] = gdf["divide_id"].str[4:].astype(int)
            gdf["catchment"] = gdf["divide_id"]  # For joining with NGen data

        elif layer == "wells":
            gdf["lon"] = gdf.geometry.x  # Extract longitude
            gdf["lat"] = gdf.geometry.y  # Extract latitude

        return gdf

    def cfe_basin_q(self) -> pd.DataFrame:
        """
        Load CFE Q from NGen simulation (and gauge observations).

        Returns:
            DataFrame: Simulated monthly volume.
        """
        # v1
        # df = self.pd_read_s3_csv(
        #     key="ngen_dr/cfe_calib_valid_2024_10_07/output_sim_obs/sim_obs_validation.csv",
        # )
        # df.index = pd.to_datetime(df["time"])
        # df = df[["sim_flow"]]
        # # Convert daily streamflow (m³/s) to volume per day (m³/day)
        # df["Simulated Monthly Volume"] = (
        #     df["sim_flow"] * 86400  # UNIT
        # )  # 86400 seconds in a day
        # df = df.resample("MS").sum()
        # return df[["Simulated Monthly Volume"]]

        # v2
        # ds = xr.open_dataset(
        #     "/Users/dillonragar/data/tnc/cfe_valid_2024_11_03/output_300/troute_output_198109300000.nc"
        # )

        # df = ds.sel({"feature_id": 23})["flow"].to_pandas()
        # df *= 3600
        # df = df.resample("MS").sum()

        # df_out = pd.DataFrame(df)

        df = self.pd_read_s3_parquet(
            key="webapp_resources/cfe_20241103_troute_cat23.parquet"
        )
        return df[["flow"]]

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
            pd.read_csv(p, index_col=["Time"], parse_dates=["Time"]) for p in cat_paths
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
        Pulls NetCDF from S3 as an xarray Dataset, formatted for the web app.

        Args:
            key (str): S3 key for the NetCDF file.

        Returns:
            Dataset: xarray Dataset.
        """
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        file_stream = io.BytesIO(response["Body"].read())

        ds = xr.open_dataset(file_stream, engine="scipy")
        ds = ds.sel(Time=slice("1982-10-01", None))
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
            df["weighted_tnc_flow"] * 0.0283  # UNIT
        )  # Convert cfs to m³/day

        # Group by 'divide_id' and resample to monthly (resulting in m³ per month)
        resampled_df = (
            df.groupby("divide_id")
            .resample("MS")
            .agg({"weighted_tnc_flow": "sum"})
            .reset_index()
        )
        resampled_df.index = pd.to_datetime(resampled_df.date)
        return resampled_df[["weighted_tnc_flow", "divide_id"]]

    def read_tnc_domain_q(self) -> pd.DataFrame:
        """
        Loads temporary full basin comparison data from S3.

        Returns:
            DataFrame: Monthly volume in m³.
        """
        df = self.pd_read_s3_csv(
            key="webapp_resources/flow_17593507_mean_estimated_1982_2023.csv",
        )

        df["monthly_vol_m3"] = df["value"] * 73271  # UNIT
        df["date"] = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
        )
        df.reset_index(inplace=True)
        df.index = df["date"]
        df = df[["monthly_vol_m3"]]
        return df

    def get_outline(self) -> gpd.GeoDataFrame:
        """
        Reads the outline data from the data directory.

        Returns:
            GeoDataFrame: Geopandas dataframe with the outline.
        """
        filepath = os.path.join(self.data_dir, "tnc.geojson")
        gdf = gpd.read_file(filepath)
        gdf["ID"] = "dangermond preserve"
        return gdf

    # def precip_stats(self):
    #     """
    #     Parse historic water balance, or CFE results, to generate
    #     key summary statistics for use in the dashboard, including
    #     the text descriptions.

    #     This should return data for all years, year specific logic
    #     should go in `home.update_summary_text()`
    #     """
    #     # calculate mean rainfall (rain-year)
    #     df = self.terraclim["ppt"]
    #     # to monthly mean of all catchmens
    #     domain_vals = df.groupby("date")["value"].mean()  # .reset_index()
    #     self.terraclim_ann_precip = domain_vals.groupby(domain_vals.index.year).sum()
    #     self.terraclim_ann_precip = self.terraclim_ann_precip.loc["1981":]

    #     # Compute quartiles for precipitation accumulation
    #     quartile = pd.qcut(
    #         self.terraclim_ann_precip,
    #         q=5,
    #         labels=[
    #             "a far below average",
    #             "a below average",
    #             "a near average",
    #             "an above average",
    #             "a far above average",
    #         ],
    #     )

    #     # Attach quartiles as a DataFrame with precipitation values for reference
    #     self.terraclim_ann_precip = pd.DataFrame(
    #         {"Annual Precip (mm)": self.terraclim_ann_precip, "Quartile": quartile}
    #     )

    #     self.terraclim_mean_annual_precip = self.terraclim_ann_precip[
    #         "Annual Precip (mm)"
    #     ].mean()

    #     # sum of rain-year precip for `rain_year`
    #     # ry_ppt_sum = domain_val[rain_year[0] : rain_year[1]].sum()

    #     # mean annual change in storage (inflow - outflow)

    #     # total precip (rain year)

    #     # total annual inflow

    #     # total

    def precip_stats(self):
        """
        Parse historic water balance, or CFE results, to generate
        key summary statistics for use in the dashboard, including
        the text descriptions.

        This should return data for all years, year-specific logic
        should go in `home.update_summary_text()`.
        """
        # Access precipitation data
        df = self.terraclim["ppt"]

        # Create a new column for water year
        df["water_year"] = df.index.year.where(df.index.month < 10, df.index.year + 1)

        # Group by water year and calculate annual precipitation totals
        domain_vals = df.groupby("water_year")["value"].mean()
        self.terraclim_ann_precip = domain_vals.groupby(domain_vals.index).sum()
        self.terraclim_ann_precip = self.terraclim_ann_precip.loc["1982":]

        # Compute quartiles for precipitation accumulation
        quartile = pd.qcut(
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
            {"Annual Precip (mm)": self.terraclim_ann_precip, "Quartile": quartile}
        )

        self.terraclim_mean_annual_precip = self.terraclim_ann_precip[
            "Annual Precip (mm)"
        ].mean()

    def ngen_stats(self):
        """
        process and aggregate ngen simulation for visualizations
        """
        df = pd.DataFrame()

        df["DEEP_GW_TO_CHANNEL"] = (
            self.ds_ngen["DEEP_GW_TO_CHANNEL_FLUX"].mean("catchment").to_pandas()
        )
        df["SOIL_TO_GW_FLUX"] = (
            self.ds_ngen["SOIL_TO_GW_FLUX"].mean("catchment").to_pandas()
        )
        df["SOIL_STORAGE"] = self.ds_ngen["SOIL_STORAGE"].mean("catchment").to_pandas()

        df["net"] = df["SOIL_TO_GW_FLUX"] - df["DEEP_GW_TO_CHANNEL"]

        df *= 3.2808  # UNIT meters to feet

        self.gw_net = df
        self.gw_delta_yr = df.resample("YE").sum()

    def ngen_gw_vol(self):
        """Calculate storage based on groundwater infiltration and outflow to channel"""
        # Get the list of catchments present in the dataset
        # Conversion factor from cubic feet to acre-feet
        # Conversion factor from km² to ft²
        SQKM_TO_SQFT = 1e6 * 10.7639
        FT3_TO_ACRE_FT = 1 / 43560

        dataset_catchments = self.ds_ngen["catchment"].values

        # Filter the GeoDataFrame to include only catchments that exist in the dataset
        catchment_areas = (
            self.gdf_lines.set_index("divide_id")
            .loc[dataset_catchments, "areasqkm"]  # Select only relevant catchments
            .dropna()  # Drop any missing values to avoid mismatches
        )

        # Ensure the index name matches the dataset dimension name
        catchment_areas.index.name = "catchment"

        # Convert to an xarray DataArray with matching coordinates
        catchment_areas_xr = xr.DataArray(
            catchment_areas,
            coords={"catchment": catchment_areas.index},
            dims="catchment",
        )

        # Add it to the dataset
        self.ds_ngen["areasqkm"] = catchment_areas_xr

        # Ensure areasqkm is in the correct units (square feet)
        self.ds_ngen["area_sqft"] = self.ds_ngen["areasqkm"] * SQKM_TO_SQFT

        # compute total volume (ft³/month) for each catchment
        self.ds_ngen["SOIL_TO_GW_VOL"] = (
            self.ds_ngen["SOIL_TO_GW_FLUX"] * self.ds_ngen["area_sqft"]
        )
        self.ds_ngen["DEEP_GW_TO_CHANNEL_VOL"] = (
            self.ds_ngen["DEEP_GW_TO_CHANNEL_FLUX"] * self.ds_ngen["area_sqft"]
        )

        self.ds_ngen["NET_VOL"] = (
            self.ds_ngen["SOIL_TO_GW_VOL"] - self.ds_ngen["DEEP_GW_TO_CHANNEL_VOL"]
        )

        # Convert NET_VOL to acre-feet
        self.ds_ngen["NET_VOL_ACRE_FT"] = self.ds_ngen["NET_VOL"] * FT3_TO_ACRE_FT

        self.ngen_basinwide_gw_storage = (
            self.ds_ngen["NET_VOL_ACRE_FT"]
            .sum(dim="catchment")
            .cumsum()
            .to_pandas()
            # .resample("YE")
            # .sum()
        )


# def text_description(self):
#     """
#     Generate a text description.

#     Example:

#     Last year was an average/above/below rain year with XX atmospheric rivers
#     events delivering XX inches of precipitation. In 2022-23 rain-year we measured
#     average XX inches of precipitation at XX weather stations XX times the
#     average rainfall of XX inches.
#     """
#     return NotImplementedError
#     description = (
#         f"Last year was an average/above/below rain year with {n_ar}atmospheric rivers"
#         "events delivering {annual_precip} inches of precipitation. In 2022-23 rain-year we measured"
#         "average {} inches of precipitation at {} weather stations {} times the"
#         "average rainfall of {} inches. "
#     )
