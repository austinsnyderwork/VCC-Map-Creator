import pyproj
from shapely.geometry import Point


def convert_crs(df):
    # Setup projection: WGS84 to UTM Zone 15N (covers Iowa)
    project = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:26915", always_xy=True).transform

    # Replace visiting/origin lat/lon with projected x/y (in meters)
    df["visiting_x"], df["visiting_y"] = zip(*df.apply(
        lambda row: project(row["visiting_lon"], row["visiting_lat"]),
        axis=1
    ))

    df["origin_x"], df["origin_y"] = zip(*df.apply(
        lambda row: project(row["origin_lon"], row["origin_lat"]),
        axis=1
    ))

    return df