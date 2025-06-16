import pandas as pd


def _apply_change_city_names(row, city_name_changes: dict, cities_lookup: dict):
    if row['origin_city'] in city_name_changes:
        new_name = city_name_changes[row['origin_city']]
        lon, lat = cities_lookup[new_name]
        row['origin_city'] = new_name
        row['origin_lon'] = lon
        row['origin_lat'] = lat

    if row['visiting_city'] in city_name_changes:
        new_name = city_name_changes[row['visiting_city']]
        lon, lat = cities_lookup[new_name]
        row['visiting_city'] = new_name
        row['visiting_lon'] = lon
        row['visiting_lat'] = lat

    return row


def build_city_coord_lookup(df: pd.DataFrame) -> dict:
    origin_df = df[['origin_city', 'origin_lon', 'origin_lat']].rename(
        columns={'origin_city': 'city', 'origin_lon': 'lon', 'origin_lat': 'lat'}
    )
    visiting_df = df[['visiting_city', 'visiting_lon', 'visiting_lat']].rename(
        columns={'visiting_city': 'city', 'visiting_lon': 'lon', 'visiting_lat': 'lat'}
    )

    combined = pd.concat([origin_df, visiting_df], ignore_index=True)
    combined = combined.drop_duplicates(subset='city')

    return dict(zip(combined['city'], zip(combined['lon'], combined['lat'])))


def change_city_names(vcc_df: pd.DataFrame, city_name_changes: dict):
    cities_lookup = build_city_coord_lookup(vcc_df)

    vcc_df = vcc_df.apply(_apply_change_city_names, axis=1, args=(city_name_changes, cities_lookup))

    return vcc_df