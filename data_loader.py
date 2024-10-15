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
    read geopackage from s3 bucket as geopandas df
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
            key=f"water_balance/v2/cabcm/{var}.parquet",
            bucket="tnc-dangermond",
        )
        df.index = pd.to_datetime(df["date"])
        all_vars[var] = df

    return all_vars


# def get_s3_hydrofabric():
#     """
#     get Dangermond hydrofabric
#     """
#     gdf = gpd_read_s3_gpk(
#         bucket="tnc-dangermond", key="refactor_hydrofabric.gpkg", s3_client=s3
#     )
#     # gdf["comid"] = gdf["comid"].astype(int)
#     gdf = gdf.to_crs("EPSG:4326")
#     return gdf


def get_local_hydrofabric(layer):
    """Read from data dir

    kwargs for gpd.read_file can be supplied, such as layer_name for
    multilayere geopackages.

    TEMP METHOD for standin data
    """
    gdf = gpd.read_file("./data/jldp_ngen_nhdhr.gpkg", layer=layer)
    gdf = gdf.to_crs("EPSG:4326")

    if layer == "divides":
        gdf["feature_id"] = gdf["divide_id"].str[4:].astype(int)
        gdf["catchment"] = gdf["divide_id"]  # for joining w/ ngen data

    elif layer == "wells":
        gdf["lon"] = gdf.geometry.x  # Extract longitude
        gdf["lat"] = gdf.geometry.y  # Extract latitude

    return gdf


def ngen_basin_q():
    """Q from NexGen simulation (and gage obs)"""
    # df = pd.read_csv(
    #     "/Users/dillonragar/github/tnc_webapp/data/sim_obs_validation.csv",
    #     index_col="time",
    # )

    df = pd_read_s3_csv(
        s3_client=s3,
        bucket="tnc-dangermond",
        key="ngen_dr/cfe_calib_valid_2024_10_07/output_sim_obs/sim_obs_validation.csv",
    )
    df.index = pd.to_datetime(df["time"])
    df = df[["sim_flow"]]
    # Convert daily streamflow (m³/s) to volume per day (m³/day)
    df["Simulated Monthly Volume"] = (
        df["sim_flow"] * 86400
    )  # UNIT: 86400 seconds in a day
    df = df.resample("MS").sum()

    return df[["Simulated Monthly Volume"]]


# def get_local_routing():
#     """
#     temp method for placeholder data
#     """
#     df = pd.read_csv(
#         "/Users/dillonragar/data/tnc/fake_data/datastream_test/ngen-run/outputs/troute/troute_output_202006150100.csv"
#     )
#     # create timestamp col
#     df["t0"] = pd.to_datetime(df["t0"])
#     df["time"] = pd.to_timedelta(df["time"])
#     df["timestamp"] = df["t0"] + df["time"]
#     # make index and rm
#     df.index = df["timestamp"]
#     df.drop(columns="timestamp", inplace=True)

#     return df


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


def ngen_csv_to_xr(path, cats_out=False):
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

    if cats_out:
        return ds, cats

    return ds


def ngen_dashboard_data(s3_client, bucket_name, key):
    """Pulls NetCDF from s3 as xarray object, with data that has been
    previously reformatted from the raw ngen output to an aggregated
    format for display on the web app.

    """
    # using meta.client workaround
    response = s3_client.meta.client.get_object(Bucket=bucket_name, Key=key)
    file_stream = io.BytesIO(response["Body"].read())

    ds = xr.open_dataset(
        file_stream, engine="scipy"
    )  # only works with "scipy" engine as of testing, for file
    # produce by xarray 2024.7.0
    return ds


def monthly_gw_delta(filepath):
    """Load monthly goundwater delta

    Parameters:
    filepath (str): directory with each station delta as Parquet

    Returns:
    gw_deltas (dict): dict with where k: stn id and v: dataframe
    """
    directory = Path(filepath)
    files = [file for file in directory.rglob("*.parquet") if "monthly" in file.name]

    gw_deltas = {}

    for f in files:
        df = pd.read_parquet(f)
        stn_id = df["stn_id_dendra"].iloc[0]
        gw_deltas[stn_id] = df

    return gw_deltas


def natural_flows():
    """
    s3 now.
    """
    # df = pd.read_parquet("/Users/dillonragar/Downloads/weighted_natural_flows.parquet")
    df = pd_read_s3_parquet(
        bucket="tnc-dangermond",
        key="water_balance/tnc/weighted_natural_flows.parquet",
        s3_client=s3,
    )

    df.index = pd.to_datetime(df["date"])
    df["divide_id"] = df["divide_id"].astype(int)

    df["weighted_tnc_flow"] = (
        df["weighted_tnc_flow"] * 0.0283
    )  # UNIT: cfs to m^3 per day

    # UNIT: Group by 'divide_id' and resample to monthly (resuluting in m^3 per month)
    resampled_df = (
        df.groupby("divide_id")
        .resample("MS")
        .agg({"weighted_tnc_flow": "sum"})
        .reset_index()
    )
    resampled_df.index = pd.to_datetime(resampled_df.date)
    return resampled_df[["weighted_tnc_flow", "divide_id"]]


def read_tnc_domain_q():
    """
    s3

    Temporary full basin comparison, downloaded from Natural Flows.
    """
    # df = pd.read_csv(
    #     "/Users/dillonragar/data/tnc/flow_17593507_mean_estimated_1982_2023.csv"
    # )
    df = pd_read_s3_csv(
        bucket="tnc-dangermond",
        key="webapp_resources/flow_17593507_mean_estimated_1982_2023.csv",
        s3_client=s3,
    )

    df["monthly_vol_m3"] = df["value"] * 73271  # UNIT
    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str) + "-01"
    )
    df.reset_index(inplace=True)
    df.index = df["date"]
    df = df[["monthly_vol_m3"]]
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
