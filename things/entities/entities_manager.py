from typing import Callable

from things.thing_container import ThingContainer
from things.entities import entities


def _generate_key(entity_type, **kwargs):
    if entity_type is entities.City:
        return entities.City, kwargs['name']
    elif entity_type is entities.ProviderAssignment:
        return entities.ProviderAssignment, kwargs['origin_site_name'], kwargs['visiting_site_name']
    elif entity_type is entities.VccClinicSite:
        return entities.VccClinicSite, kwargs['city_name'], kwargs['name']
    elif entity_type is entities.Provider:
        return entities.Provider, kwargs['name']


class EntitiesManager:

    def __init__(self):
        self.entities_containers = {
            entities.City: ThingContainer(generate_key_func=_generate_key),
            entities.ProviderAssignment: ThingContainer(generate_key_func=_generate_key),
            entities.VccClinicSite: ThingContainer(generate_key_func=_generate_key),
            entities.Provider: ThingContainer(generate_key_func=_generate_key)
        }

    def add_entity(self, entity: entities.Entity):
        entities_container = self.entities_containers[type(entity)]
        entities_container.add_thing(thing=entity)

    def get_city(self, name: str):
        container = self.entities_containers[entities.City]
        return entity_dict.get_thing(entities.City, name=name)

    def get_vcc_clinic_site(self, name: str, city_name: str):
        entity_dict = self.entities_containers[entities.VccClinicSite]
        return entity_dict.get_thing(entities.VccClinicSite, name=name, city_name=city_name)

    def get_provider(self, name: str):
        entity_dict = self.entities_containers[entities.Provider]
        return entity_dict.get_thing(entities.VccClinicSite, name=name)

    def contains_entity(self, entity_type, **kwargs):
        key = _generate_key(entity_type=entity_type, **kwargs)
        return key in self.entities_containers





