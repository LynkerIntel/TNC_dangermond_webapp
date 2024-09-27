import pandas as pd
import numpy as np
import xarray as xr
import boto3
import io
import geopandas as gpd
import shapely.geometry
import os
from pathlib import Path


# initialize boto3 S3 client
# s3 = boto3.client("s3")

# note, boto3 will ignore this if local aws credentials exist
s3 = boto3.resource(
    "s3",
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
)


# Read single parquet file from S3
def pd_read_s3_parquet(key, bucket, s3_client=None, **args):
    """ """
    if s3_client is None:
        s3_client = boto3.client("s3")
    obj = s3_client.meta.client.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(io.BytesIO(obj["Body"].read()), **args)


def pd_read_s3_csv(key, bucket, s3_client=None, **args):
    """ """
    if s3_client is None:
        s3_client = boto3.client("s3")
    obj = s3_client.meta.client.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj["Body"].read()), **args)


def gpd_read_s3_gpk(s3_client, key, bucket, driver="GPKG", **args):
    """
    read geopandas dataframe from s3 bucket
    """

    response = s3_client.meta.client.get_object(Bucket=bucket, Key=key)

    data = response["Body"].read()

    with io.BytesIO(data) as src:
        gdf = gpd.read_file(src, driver=driver)

    return gdf


def get_s3_cabcm():
    """
    load California Basin Characterization Model summarization from s3

    :returns (dict): dict of pd.dataframe for each var
    """
    model_vars = ["aet", "cwd", "pck", "pet", "rch", "run", "str", "tmn", "tmx"]
    all_vars = {}

    for var in model_vars:
        df = pd_read_s3_parquet(
            s3_client=s3,
            key=f"water_balance/cabcm/{var}.parquet",
            bucket="tnc-dangermond",
        )
        df.index = pd.to_datetime(df["date"])
        all_vars[var] = df

    return all_vars


def get_s3_hydrofabric():
    """
    get Dangermond hydrofabric
    """
    gdf = gpd_read_s3_gpk(
        bucket="tnc-dangermond", key="refactor_hydrofabric.gpkg", s3_client=s3
    )
    # gdf["comid"] = gdf["comid"].astype(int)
    gdf = gdf.to_crs("EPSG:4326")
    return gdf


def get_local_hydrofabric():
    """Read from data dir

    kwargs for gpd.read_file can be supplied, such as layer_name for
    multilayere geopackages.

    TEMP METHOD for standin data
    """
    gdf = gpd.read_file("./data/jldp_ngen_nhdhr.gpkg", layer="divides")
    gdf = gdf.to_crs("EPSG:4326")
    # print(gdf)
    gdf["feature_id"] = gdf["divide_id"].str[4:].astype(int)
    gdf["catchment"] = gdf["divide_id"]  # for joining w/ ngen data
    return gdf


def get_local_basin_q():
    """Q from NexGen simulation (and gage obs)"""
    df = pd.read_csv(
        "/Users/dillonragar/data/tnc/output_2024_09_26/output_sim_obs/sim_obs_24.csv",
        index_col="time",
    )
    df.index = pd.to_datetime(df.index)
    df = df[["sim_flow", "obs_flow"]]
    return df


def get_local_routing():
    """
    temp method for placeholder data
    """
    df = pd.read_csv(
        "/Users/dillonragar/data/tnc/fake_data/datastream_test/ngen-run/outputs/troute/troute_output_202006150100.csv"
    )
    # create timestamp col
    df["t0"] = pd.to_datetime(df["t0"])
    df["time"] = pd.to_timedelta(df["time"])
    df["timestamp"] = df["t0"] + df["time"]
    # make index and rm
    df.index = df["timestamp"]
    df.drop(columns="timestamp", inplace=True)

    return df


def ngen_csv_to_df(path):
    """Loads nexgen csv outputs

    Parameters
    path (str): locations in nexgen output with catchment .csv files
    """
    cat_paths = list(Path(path).glob("cat-*.csv"))

    catchments = [p.stem for p in cat_paths]
    df_lst = [
        pd.read_csv(p, index_col=["Time"], parse_dates=["Time"]) for p in cat_paths
    ]
    # myDict = {k: pd.read_csv(v, index_col=["Time"]) for (k, v) in zip(cats, cat_paths)}

    return df_lst, catchments


def ngen_df_to_xr(path):
    """Method to parse nexgen model outputs"""

    # get ngen output as list of dfs and names
    df_lst, cats = ngen_csv_to_df(path)

    data_vars = {}

    # Loop through each DataFrame and each variable (column) to create DataArrays
    for df, catchment in zip(df_lst, cats):
        for column in df.columns:
            if column not in data_vars:
                # Initialize a list for this variable if not already present
                data_vars[column] = []
            # Create a DataArray for each variable and append it, ensuring we capture catchment name
            data_vars[column].append(
                xr.DataArray(
                    df[column].values,
                    dims=["Time"],
                    coords={"Time": df.index},  # Only time for now
                )
            )

    # Concatenate each variable's DataArrays along the 'catchment' dimension
    for var in data_vars:
        # Concatenate across the catchment dimension using the "cats" list for catchment names
        data_vars[var] = xr.concat(data_vars[var], dim=pd.Index(cats, name="catchment"))

    # Now, create the final dataset
    ds = xr.Dataset(data_vars)
    return ds


def get_outline():
    """ """
    gdf = gpd.read_file("./data/tnc.geojson")
    gdf["ID"] = "dangermond preserve"
    return gdf


def mapbox_line_gdf_fmt(gdf, id_col="ID"):
    """ """
    lats = []
    lons = []
    names = []

    for feature, name in zip(gdf.geometry, gdf[id_col]):
        if isinstance(feature, shapely.geometry.linestring.LineString):
            linestrings = [feature]
        elif isinstance(feature, shapely.geometry.multilinestring.MultiLineString):
            linestrings = feature.geoms
        else:
            continue
        for linestring in linestrings:
            x, y = linestring.xy
            lats = np.append(lats, y)
            lons = np.append(lons, x)
            names = np.append(names, [name] * len(y))
            lats = np.append(lats, None)
            lons = np.append(lons, None)
            names = np.append(names, None)

    return lats, lons, names
