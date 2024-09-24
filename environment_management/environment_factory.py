import pandas as pd
from typing import Callable

import entities
from .environment import Environment


def _flatten_dict(dict_: dict):
    new_dict = {}
    for key, value_list in dict_:
        for value in value_list:
            new_dict[value] = key
    return new_dict


class EnvironmentFactory:

    def __init__(self, environment: Environment, df: pd.DataFrame):
        self.environment = environment
        self.df = df

        self.environment_filled = False

    def _apply_create_cities(self, row, coord_converter: Callable, city_name_changes: dict):
        origin_city_name = row['point_of_origin']
        origin_city_name = city_name_changes[origin_city_name] if origin_city_name in city_name_changes else origin_city_name
        origin_lon, origin_lat = coord_converter(row['origin_lon'], row['origin_lat'])
        origin_city = entities.City(name=origin_city_name,
                                    coord=(origin_lon, origin_lat))
        self.environment.add_city(origin_city)

        outpatient_city_name = row['community']
        outpatient_city_name = city_name_changes[
            outpatient_city_name] if outpatient_city_name in city_name_changes else outpatient_city_name
        outpatient_lon, outpatient_lat = coord_converter(row['outpatient_lon'], row['outpatient_lat'])
        outpatient_city = entities.City(name=outpatient_city_name,
                                        coord=(outpatient_lon, outpatient_lat))
        self.environment.add_city(outpatient_city)

    def _apply_create_clinic_sites(self, row, created_clinic_names: set):
        origin_clinic_name = row['clinic_site']
        origin_city_coord = row['origin_lon'], row['origin_lat']

        if origin_clinic_name not in created_clinic_names:
            origin_clinic = entities.VccClinicSite(name=origin_clinic_name,
                                                   city_name=row['point_of_origin'],
                                                   city_coord=origin_city_coord)
            self.environment.add_clinic(clinic=origin_clinic,
                                        direction='leaving')
            created_clinic_names.add(origin_clinic_name)

        outpatient_clinic_name = row['group']
        outpatient_city_coord = row['to_lon'], row['to_lat']
        if outpatient_clinic_name not in created_clinic_names:
            outpatient_clinic = entities.VccClinicSite(name=outpatient_clinic_name,
                                                       city_name=row['community'],
                                                       city_coord=outpatient_city_coord)
            self.environment.add_clinic(clinic=outpatient_clinic,
                                        direction='visiting')
            created_clinic_names.add(outpatient_clinic_name)

    def _apply_create_providers(self, row):
        new_provider = entities.Provider(name=row['consultant'],
                                         specialty=row['specialty'])
        self.environment.add_provider(new_provider,
                                      origin_site_name=row['group'],
                                      outpatient_site_name=row['clinic_site'])

    def fill_environment(self, coord_converter: Callable, city_name_changes: dict):
        city_name_changes = _flatten_dict(city_name_changes)
        self.df.apply(self._apply_create_cities, coord_converter=coord_converter,
                      city_name_changes=city_name_changes, axis=1)

        self.df.apply(self._apply_create_clinic_sites, axis=1)

        self.df.apply(self._apply_create_providers, axis=1)

        self.environment_filled = True
