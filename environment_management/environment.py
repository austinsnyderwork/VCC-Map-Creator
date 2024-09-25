from . import entities
import environment_management
from .worksite_grouping import CityOriginNetworkHandler


def _generate_key(entity_type, **kwargs):
    if entity_type is entities.VccClinicSite:
        return entities.VccClinicSite, kwargs['name'], kwargs['city_name']
    elif entity_type is entities.City:
        return entities.City, kwargs['name']
    elif entity_type is entities.Provider:
        return entities.Provider, kwargs['name']


class Environment:

    def __init__(self, cities_directory: environment_management.CitiesDirectory,
                 city_origin_network_handler: CityOriginNetworkHandler):
        self.cities_directory = cities_directory
        self.origin_groups_handler = city_origin_network_handler

        self.entities = {}

    def add_entity(self, entity: entities.Entity):
        key = _generate_key(entity_type=type(entity), kwargs=entity.__dict__)
        self.entities[key] = entity

        if type(entity) is entities.City:
            self.cities_directory.add_city(entity)

    def get_city(self, name: str):
        key = _generate_key(entities.City, name=name)
        return self.entities[key]

    def get_vcc_clinic_site(self, name: str, city_name: str):
        key = _generate_key(entities.VccClinicSite, name=name, city_name=city_name)
        return self.entities[key]

    def get_provider(self, name: str):
        key = _generate_key(entities.Provider, name=name)
        return self.entities[key]

    def contains_entity(self, entity_type, **kwargs):
        key = _generate_key(entity_type=entity_type, **kwargs)
        return key in self.entities





