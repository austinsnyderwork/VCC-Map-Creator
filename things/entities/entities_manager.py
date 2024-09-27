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

    def get_all_entities(self, entities_type: entities.Entity = None, entities_types: list[entities.Entity] = None):
        if entities_type:
            container = self.entities_containers[entities_type]
            entities_ = container.get_all_things()
        elif entities_types:
            entities_ = []
            for entity_type in entities_types:
                entities_.extend(self.get_all_entities(entities_type=entity_type))
        return entities_

    def add_entity(self, entity: entities.Entity):
        entities_container = self.entities_containers[type(entity)]
        entities_container.add_thing(thing=entity)

    def get_city(self, name: str):
        container = self.entities_containers[entities.City]
        return container.get_thing(entities.City, name=name)

    def get_vcc_clinic_site(self, name: str, city_name: str):
        container = self.entities_containers[entities.VccClinicSite]
        return container.get_thing(entities.VccClinicSite, name=name, city_name=city_name)

    def get_provider(self, name: str):
        container = self.entities_containers[entities.Provider]
        return container.get_thing(entities.VccClinicSite, name=name)

    def contains_entity(self, entity_type, **kwargs):
        key = _generate_key(entity_type=entity_type, **kwargs)
        return key in self.entities_containers





