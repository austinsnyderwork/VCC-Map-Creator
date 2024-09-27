import pandas as pd
from typing import Callable

from things.entities import entities
from things.entities import entities_manager


def _apply_create_cities(row, coord_converter, cities: dict):
    origin_city_name = row['origin_city']
    origin_lon, origin_lat = coord_converter(coord=(row['origin_lon'], row['origin_lat']))
    if origin_city_name not in cities:
        origin_city = entities.City(name=origin_city_name,
                                    coord=(origin_lon, origin_lat))
        key = entities_manager.generate_key(origin_city, **origin_city.__dict__)
        cities[key] = origin_city

    visiting_city_name = row['visiting_city']
    visiting_lon, visiting_lat = coord_converter(coord=(row['visiting_lon'], row['visiting_lat']))
    if visiting_city_name not in cities:
        visiting_city = entities.City(name=visiting_city_name,
                                      coord=(visiting_lon, visiting_lat))
        key = entities_manager.generate_key(visiting_city, **visiting_city.__dict__)
        cities[key] = visiting_city


def _apply_create_clinic_sites(row, clinics: dict):
    origin_clinic_name = row['origin_site']
    origin_city_name = row['origin_city']
    origin_city_coord = row['origin_lon'], row['origin_lat']

    key = entities_manager.generate_key(entity_type=entities.VccClinicSite,
                                        name=origin_clinic_name)
    if key not in clinics:
        origin_clinic = entities.VccClinicSite(name=origin_clinic_name,
                                               city_name=origin_city_name,
                                               city_coord=origin_city_coord)
        clinics[key] = origin_clinic

    visiting_clinic_name = row['visiting_site']
    visiting_city_name = row['visiting_city']
    visiting_city_coord = row['visiting_lon'], row['visiting_lat']
    key = entities_manager.generate_key(entity_type=entities.VccClinicSite,
                                        name=visiting_clinic_name)
    if key not in clinics:
        visiting_clinic = entities.VccClinicSite(name=visiting_clinic_name,
                                                 city_name=visiting_city_name,
                                                 city_coord=visiting_city_coord)
        clinics[key] = visiting_clinic


def _apply_create_provider_assignments(row, provider_assignments: dict, providers: dict):
    provider_name = row['consultant_name']
    origin_clinic_name = row['origin_site']
    origin_city_name = row['origin_city']

    visiting_clinic_name = row['visiting_site']
    visiting_city_name = row['visiting_city']

    if provider_name not in providers:
        provider = entities.Provider(name=provider_name)
        providers[provider_name] = provider

    provider = providers[provider_name]

    specialty = row['specialty']
    new_provider_assignment = entities.ProviderAssignment(provider=provider,
                                                          specialty=specialty,
                                                          origin_site_name=origin_clinic_name,
                                                          origin_city_name=origin_city_name,
                                                          visiting_site_name=visiting_clinic_name,
                                                          visiting_city_name=visiting_city_name)
    key = entities_manager.generate_key(entities.ProviderAssignment,
                                        **new_provider_assignment.__dict__)
    provider_assignments[key] = new_provider_assignment


class EntitiesFactory:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_entities(self, coord_converter: Callable):
        cities = {}
        self.df.apply(_apply_create_cities, coord_converter=coord_converter, cities=cities, axis=1)

        clinics = {}
        self.df.apply(_apply_create_clinic_sites, entities_manager=entities_manager, clinics=clinics)

        provider_assignments = {}
        providers = {}
        self.df.apply(_apply_create_provider_assignments, provider_assignments=provider_assignments,
                      providers=providers)

        return {
            entities.City: list(cities.values()),
            entities.VccClinicSite: list(clinics.values()),
            entities.ProviderAssignment: list(provider_assignments.values())
        }
