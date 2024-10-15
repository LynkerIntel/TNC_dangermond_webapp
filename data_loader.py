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
    def __init__(
        self, bucket_name, s3_resource=None, data_dir="./data/", ngen_output_dir=None
    ):
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

    def get_s3_cabcm(self):
        """
        Load California Basin Characterization Model summarization from S3.

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

    def get_local_hydrofabric(self, layer):
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

    def ngen_basin_q(self):
        """
        Load Q from NGen simulation (and gauge observations).

        Returns:
            DataFrame: Simulated monthly volume.
        """
        df = self.pd_read_s3_csv(
            key="ngen_dr/cfe_calib_valid_2024_10_07/output_sim_obs/sim_obs_validation.csv",
        )
        df.index = pd.to_datetime(df["time"])
        df = df[["sim_flow"]]
        # Convert daily streamflow (m³/s) to volume per day (m³/day)
        df["Simulated Monthly Volume"] = (
            df["sim_flow"] * 86400
        )  # 86400 seconds in a day
        df = df.resample("MS").sum()

        return df[["Simulated Monthly Volume"]]

    def ngen_csv_to_df(self, path=None):
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

    def ngen_csv_to_xr(self, path=None, cats_out=False):
        """
        Parses NGen model outputs into an xarray Dataset.

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

    def ngen_dashboard_data(self, key):
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
        return ds

    def monthly_gw_delta(self, prefix):
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
            if key.endswith(".parquet"):
                obj_body = obj.get()["Body"].read()
                parquet_buffer = io.BytesIO(obj_body)
                df = pd.read_parquet(parquet_buffer)
                stn_id = df["stn_id_dendra"].iloc[0]
                parquet_dfs[stn_id] = df

        return parquet_dfs

    def natural_flows(self):
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

    def read_tnc_domain_q(self):
        """
        Loads temporary full basin comparison data from S3.

        Returns:
            DataFrame: Monthly volume in m³.
        """
        df = self.pd_read_s3_csv(
            key="webapp_resources/flow_17593507_mean_estimated_1982_2023.csv",
        )

        df["monthly_vol_m3"] = df["value"] * 73271
        df["date"] = pd.to_datetime(
            df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
        )
        df.reset_index(inplace=True)
        df.index = df["date"]
        df = df[["monthly_vol_m3"]]
        return df

    def get_outline(self):
        """
        Reads the outline data from the data directory.

        Returns:
            GeoDataFrame: Geopandas dataframe with the outline.
        """
        filepath = os.path.join(self.data_dir, "tnc.geojson")
        gdf = gpd.read_file(filepath)
        gdf["ID"] = "dangermond preserve"
        return gdf
