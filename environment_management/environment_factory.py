import pandas as pd
from typing import Callable

from things.entities import entities
from .environment import Environment


def _apply_create_cities(row, environment, coord_converter):
    origin_city_name = row['point_of_origin']
    origin_lon, origin_lat = coord_converter(row['origin_lon'], row['origin_lat'])
    if not environment.contains_entity(entities.City, name=origin_city_name):
        origin_city = entities.City(name=origin_city_name,
                                    coord=(origin_lon, origin_lat))
        environment.add_entity(origin_city)

    outpatient_city_name = row['community']
    outpatient_lon, outpatient_lat = coord_converter(row['outpatient_lon'], row['outpatient_lat'])
    if not environment.contains_entity(entities.City, name=outpatient_city_name):
        outpatient_city = entities.City(name=outpatient_city_name,
                                        coord=(outpatient_lon, outpatient_lat))
        environment.add_entity(outpatient_city)


def _apply_create_clinic_sites(row, environment: Environment):
    origin_clinic_name = row['clinic_site']
    origin_city_coord = row['origin_lon'], row['origin_lat']

    if not environment.contains_entity(entities.VccClinicSite, name=origin_clinic_name):
        origin_clinic = entities.VccClinicSite(name=origin_clinic_name,
                                               city_name=row['point_of_origin'],
                                               city_coord=origin_city_coord)
        city = environment.get_city(name=origin_clinic.city_name)
        city.add_clinic_site(origin_clinic)
        environment.add_entity(entity=origin_clinic)

    outpatient_clinic_name = row['group']
    outpatient_city_coord = row['to_lon'], row['to_lat']
    if not environment.contains_entity(entities.VccClinicSite, name=outpatient_clinic_name):
        outpatient_clinic = entities.VccClinicSite(name=outpatient_clinic_name,
                                                   city_name=row['point_of_outpatient'],
                                                   city_coord=outpatient_city_coord)
        city = environment.get_city(name=outpatient_clinic.city_name)
        city.add_clinic_site(outpatient_clinic)
        environment.add_entity(outpatient_clinic)


def _apply_create_providers(row, environment: Environment):
    origin_clinic_name = row['origin_site']
    origin_city_name = row['origin_city']

    visiting_clinic_name = row['visiting_clinic']
    visiting_city_name = row['visiting_city']
    if not environment.contains_entity(entities.Provider, name=row['consultant'], specialty=row['specialty']):
        provider = entities.Provider(name=row['consultant'])
        environment.add_entity(provider)
    else:
        provider = environment.get_provider(name=row['consultant'])

    origin_clinic = environment.get_vcc_clinic_site(name=origin_clinic_name, city_name=origin_city_name)
    origin_clinic.add_provider(provider, direction='leaving')

    visiting_clinic = environment.get_vcc_clinic_site(name=visiting_clinic_name, city_name=visiting_city_name)
    visiting_clinic.add_provider(provider, direction='visiting')


class EnvironmentFactory:

    def __init__(self):
        self.environment_filled = False

    def fill_environment(self, environment: Environment, df: pd.DataFrame, coord_converter: Callable):
        df.apply(_apply_create_cities, environment=environment, coord_converter=coord_converter, axis=1)

        df.apply(_apply_create_clinic_sites, environment=environment, axis=1)

        df.apply(_apply_create_providers, environment=environment, axis=1)

        self.environment_filled = True
