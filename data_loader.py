import pandas as pd
import numpy as np
import boto3
import io


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


def read_s3_gpd(s3_client, bucket, key, driver="GPKG"):
    """
    read geopandas dataframe from s3 bucket
    """

    response = s3_client.get_object(Bucket=bucket, Key=key)

    data = response["Body"].read()

    with io.BytesIO(data) as src:
        gdf = gpd.read_file(src, driver=driver)

    if key == Config.HUC10_PATH or Config.BOI:
        gdf.geometry = gdf.geometry.simplify(0.001)

    else:
        gdf.index = gdf["index"]  # replace int index (TODO: upload correct df to s3)
        gdf.drop(columns="index", inplace=True)

    return gdf


def get_s3_cabcm():
    """
    load California Basin Characterization Model summarization from s3
    """
    df = pd_read_s3_parquet(
        key="water_balance/cabcm/tmx.parquet",
        bucket="tnc-dangermond",
    )
    return df


def get_s3_hydrofabric():
    """
    get Dangermond hydrofabric
    """


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
