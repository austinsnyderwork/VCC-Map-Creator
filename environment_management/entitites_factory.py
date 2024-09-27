import pandas as pd
from typing import Callable

from things.entities import entities
from things.entities.entities_manager import EntitiesManager


def _apply_create_cities(row, entities_manager, coord_converter):
    origin_city_name = row['origin_city']
    origin_lon, origin_lat = coord_converter(coord=(row['origin_lon'], row['origin_lat']))
    if not entities_manager.contains_entity(entities.City, name=origin_city_name):
        origin_city = entities.City(name=origin_city_name,
                                    coord=(origin_lon, origin_lat))
        entities_manager.add_entity(origin_city)

    visiting_city_name = row['visiting_city']
    visiting_lon, visiting_lat = coord_converter(coord=(row['visiting_lon'], row['visiting_lat']))
    if not entities_manager.contains_entity(entities.City, name=visiting_city_name):
        visiting_city = entities.City(name=visiting_city_name,
                                      coord=(visiting_lon, visiting_lat))
        entities_manager.add_entity(visiting_city)


def _apply_create_clinic_sites(row, entities_manager: EntitiesManager):
    origin_clinic_name = row['clinic_site']
    origin_city_coord = row['origin_lon'], row['origin_lat']

    if not entities_manager.contains_entity(entities.VccClinicSite, name=origin_clinic_name):
        origin_clinic = entities.VccClinicSite(name=origin_clinic_name,
                                               city_name=row['origin_city'],
                                               city_coord=origin_city_coord)
        city = entities_manager.get_city(name=origin_clinic.city_name)
        city.add_clinic_site(origin_clinic)
        entities_manager.add_entity(entity=origin_clinic)

    visiting_clinic_name = row['group']
    visiting_city_coord = row['to_lon'], row['to_lat']
    if not entities_manager.contains_entity(entities.VccClinicSite, name=visiting_clinic_name):
        visiting_clinic = entities.VccClinicSite(name=visiting_clinic_name,
                                                   city_name=row['visiting_city'],
                                                   city_coord=visiting_city_coord)
        city = entities_manager.get_city(name=visiting_clinic.city_name)
        city.add_clinic_site(visiting_clinic)
        entities_manager.add_entity(visiting_clinic)


def _apply_create_providers(row, entities_manager: EntitiesManager):
    origin_clinic_name = row['origin_site']
    origin_city_name = row['origin_city']

    visiting_clinic_name = row['visiting_clinic']
    visiting_city_name = row['visiting_city']
    if not entities_manager.contains_entity(entities.Provider, name=row['consultant'], specialty=row['specialty']):
        provider = entities.Provider(name=row['consultant'])
        entities_manager.add_entity(provider)
    else:
        provider = entities_manager.get_provider(name=row['consultant'])

    origin_clinic = entities_manager.get_vcc_clinic_site(name=origin_clinic_name, city_name=origin_city_name)
    origin_clinic.add_provider(provider, direction='leaving')

    visiting_clinic = entities_manager.get_vcc_clinic_site(name=visiting_clinic_name, city_name=visiting_city_name)
    visiting_clinic.add_provider(provider, direction='visiting')


class EntitiesFactory:

    def __init__(self):
        self.entities_manager_filled = False

    def fill_entities_manager(self, entities_manager: EntitiesManager, df: pd.DataFrame, coord_converter: Callable):
        df.apply(_apply_create_cities, entities_manager=entities_manager, coord_converter=coord_converter, axis=1)

        df.apply(_apply_create_clinic_sites, entities_manager=entities_manager, axis=1)

        df.apply(_apply_create_providers, entities_manager=entities_manager, axis=1)

        self.entities_manager_filled = True
