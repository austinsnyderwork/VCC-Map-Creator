import pandas as pd
from typing import Callable

import entities
from .environment import Environment


def _apply_create_cities(row, environment: Environment, coord_converter: Callable):
    origin_city_name = row['point_of_origin']
    origin_lon, origin_lat = coord_converter(row['origin_lon'], row['origin_lat'])
    origin_city = entities.City(name=origin_city_name,
                                coord=(origin_lon, origin_lat))
    environment.add_city(origin_city)

    outpatient_city_name = row['community']
    outpatient_lon, outpatient_lat = coord_converter(row['outpatient_lon'], row['outpatient_lat'])
    outpatient_city = entities.City(name=outpatient_city_name,
                                    coord=(outpatient_lon, outpatient_lat))
    environment.add_city(outpatient_city)


def _apply_create_clinic_sites(row, environment: Environment, created_clinic_names: set):
    origin_clinic_name = row['clinic_site']
    origin_city_coord = row['origin_lon'], row['origin_lat']

    if origin_clinic_name not in created_clinic_names:
        origin_clinic = entities.VccClinicSite(name=origin_clinic_name,
                                               city_name=row['point_of_origin'],
                                               city_coord=origin_city_coord)
        environment.add_clinic(clinic=origin_clinic,
                               direction='leaving')
        created_clinic_names.add(origin_clinic_name)

    outpatient_clinic_name = row['group']
    outpatient_city_coord = row['to_lon'], row['to_lat']
    if outpatient_clinic_name not in created_clinic_names:
        outpatient_clinic = entities.VccClinicSite(name=outpatient_clinic_name,
                                                   city_name=row['community'],
                                                   city_coord=outpatient_city_coord)
        environment.add_clinic(clinic=outpatient_clinic,
                               direction='visiting')
        created_clinic_names.add(outpatient_clinic_name)


def _apply_create_providers(row, environment):
    new_provider = entities.Provider(name=row['consultant'],
                                     specialty=row['specialty'])
    environment.add_provider(new_provider,
                             origin_site_name=row['group'],
                             outpatient_site_name=row['clinic_site'])


class EnvironmentFactory:

    def __init__(self):

        self.environment_filled = False

    def fill_environment(self, environment: Environment, df: pd.DataFrame, coord_converter: Callable):
        df.apply(_apply_create_cities, environment=environment, coord_converter=coord_converter, axis=1)

        df.apply(_apply_create_clinic_sites, environment=environment, axis=1)

        df.apply(_apply_create_providers, environment=environment, axis=1)

        self.environment_filled = True
