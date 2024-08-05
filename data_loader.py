import pandas as pd
import numpy as np
import boto3
import io
import geopandas as gpd
import shapely.geometry
import os


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


def get_local_hydrofabric(**kwargs):
    """Read from data dir

    kwargs for gpd.read_file can be supplied, such as layer_name for
    multilayere geopackages.

    TEMP METHOD for standin data
    """
    gdf = gpd.read_file("./data/palisade.gpkg", **kwargs)
    gdf = gdf.to_crs("EPSG:4326")
    gdf["feature_id"] = gdf["divide_id"].str[4:].astype(int)
    return gdf


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
