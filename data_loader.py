import pandas as pd
import numpy as np
import boto3
import io
import geopandas as gpd
import shapely.geometry


# initialize boto3 S3 client
s3 = boto3.client("s3")


# Read single parquet file from S3
def pd_read_s3_parquet(key, bucket, s3_client=None, **args):
    """ """
    if s3_client is None:
        s3_client = boto3.client("s3")
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(io.BytesIO(obj["Body"].read()), **args)


def pd_read_s3_csv(key, bucket, s3_client=None, **args):
    """ """
    if s3_client is None:
        s3_client = boto3.client("s3")
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj["Body"].read()), **args)


def gpd_read_s3_gpk(s3_client, key, bucket, driver="GPKG", **args):
    """
    read geopandas dataframe from s3 bucket
    """

    response = s3_client.get_object(Bucket=bucket, Key=key)

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
    gdf = gpd.read_file("./data/refactor_hydrofabric.gpkg")
    gdf = gdf.to_crs("EPSG:4326")
    return gdf


def get_tnc_outline():
    """ """
    df = gpd.read_file("./data/tnc.geojson")
    return df


def mapbox_line_gdf_fmt(gdf):
    """ """
    lats = []
    lons = []
    names = []

    for feature, name in zip(gdf.geometry, gdf["ID"]):
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


# def get_daily_data():
#     """
#     Load processed data from s3 bucket. WARN: only columns in `./data/cols.txt` will
#     be read from the Parquet file. If additional columns are added, they will need
#     to be added to this file in order to be inlcuded in the web app. This also prevents
#     data with personally identifiable identifiers from being accidentally included in
#     the user downloads from the web app. This file includes all MROS observations. New obs are appended daily.

#     TODO: need to do thorough review of datatypes in the daily processing code. many cols are str.
#     TODO: include information about the service that runs the processing code

#     returns (pd.DataFrame): all obs with new derived col called "all.id" (0-indexed)
#     """
#     with open("./data/cols.txt", encoding="utf-8") as f:
#         # Read the contents of the file into a variable
#         cols = f.read()
#         cols = cols.replace("\n", " ").split(" ")

#     df = pd_read_s3_parquet(
#         key="mros_output.parquet", bucket="mros-output-bucket", columns=cols
#     )

#     df.rename(
#         columns={
#             "name": "phase",
#             "elevation": "elevation.m",
#             # "date_key": "date",
#         },
#         inplace=True,
#     )

#     df["elevation.m"] = df["elevation.m"].astype(float)
#     df["datetime_utc"] = pd.to_datetime(df["time"])
#     df.drop(columns=["time", "timestamp", "createdtime"], inplace=True)
#     # df["date_key"] = pd.to_datetime(df["date_key"], format="%Y_%m_%d").date()

#     # add an integer index column
#     df["all.id"] = range(len(df))
#     df["latitude"] = df["latitude"].astype(float)
#     df["longitude"] = df["longitude"].astype(float)

#     # create map coords
#     df["map_latitude"] = df["latitude"].round(3)
#     df["map_longitude"] = df["longitude"].round(3)

#     # round lat lon for public distribution
#     df["latitude"] = df["latitude"].round(2)
#     df["longitude"] = df["longitude"].round(2)

#     sigma = 0.0005
#     df["map_latitude"] = df["map_latitude"].apply(lambda x: np.random.normal(x, sigma))
#     df["map_longitude"] = df["map_longitude"].apply(
#         lambda x: np.random.normal(x, sigma)
#     )

#     df["map_latitude"] = df["map_latitude"].round(4)
#     df["map_longitude"] = df["map_longitude"].round(4)

#     # create location accuracy col
#     df.insert(loc=3, column="coordinate_accuracy", value="public version")

#     return df
