import logging

import pandas as pd

from plot_maps.city_origin_volume import CityOriginVolumeConditionsController
from program_management import operations_coordinator
from program_management.power_bi_output_formatter import PowerBiOutputFormatter

logging.basicConfig(level=logging.INFO)


def _apply_change_city_names(row, city_name_changes: dict, cities_lookup: dict):
    origin_city = row['origin_city']
    visiting_city = row['visiting_city']

    if origin_city in city_name_changes:
        city_name = city_name_changes[origin_city]
        lon, lat = cities_lookup[city_name]
        row['origin_city'] = city_name
        row['origin_lon'] = lon
        row['origin_lat'] = lat

    if visiting_city in city_name_changes:
        city_name = city_name_changes[visiting_city]
        lon, lat = cities_lookup[city_name]
        row['visiting_city'] = city_name
        row['visiting_lon'] = lon
        row['visiting_lat'] = lat

    return row


def _apply_create_cities_lookup(row, cities_lookup: dict):
    origin_city = row['origin_city']

    if origin_city not in cities_lookup:
        lon = row['origin_lon']
        lat = row['origin_lat']
        cities_lookup[origin_city] = lon, lat

    visiting_city = row['visiting_city']

    if visiting_city not in cities_lookup:
        lon = row['visiting_lon']
        lat = row['visiting_lat']
        cities_lookup[origin_city] = lon, lat


def change_city_names(vcc_df: pd.DataFrame, city_name_changes: dict):
    cities_lookup = dict()
    vcc_df.apply(_apply_create_cities_lookup, axis=1, args=(cities_lookup, ))
    vcc_df = vcc_df.apply(_apply_change_city_names, axis=1, args=(city_name_changes, cities_lookup))

    return vcc_df


vcc_file_name = "C:/Users/austisnyder/Documents/GitHub/VCC-Map-Creator/vcc_maps/vcc_joined_data.csv"
vcc_df = pd.read_csv(vcc_file_name)

city_name_changes = {
    'West Des Moines': 'Des Moines',
    'Ankeny': 'Des Moines',
    'Johnston': 'Des Moines',
    'Coralville': 'Iowa City',
    'North Liberty': 'Iowa City'
}

vcc_df = change_city_names(vcc_df, city_name_changes)

interface_ = operations_coordinator.OperationsCoordinator(vcc_df=vcc_df, city_name_changes=city_name_changes)
visual_elements = interface_.create_map(CityOriginVolumeConditionsController)

pbi_df = PowerBiOutputFormatter().create_df(visual_elements=visual_elements)
pbi_df.to_csv("C:/Users/austisnyder/programming/programming_i_o_files/pbi_output.csv")


