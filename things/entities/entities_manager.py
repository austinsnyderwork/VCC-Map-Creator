from typing import Callable, Union

from things.thing_container import ThingContainer
from things.entities import entities


def generate_key(entity_type=None, entity: entities.Entity = None, **kwargs):
    if entity:
        entity_type = type(entity)

    if entity_type is entities.City:
        return entities.City, kwargs['name']
    elif entity_type is entities.ProviderAssignment:
        return entities.ProviderAssignment, kwargs['origin_site_name'], kwargs['visiting_site_name']
    elif entity_type is entities.VccClinicSite:
        return entities.VccClinicSite, kwargs['city_name'], kwargs['name']
    elif entity_type is entities.Provider:
        return entities.Provider, kwargs['name']
    else:
        raise ValueError(f"Could not generate key for entity.\nKwargs: {kwargs}")


class EntitiesManager:

    def __init__(self):
        self.entities_containers = {
            entities.City: ThingContainer(generate_key_func=generate_key),
            entities.ProviderAssignment: ThingContainer(generate_key_func=generate_key),
            entities.VccClinicSite: ThingContainer(generate_key_func=generate_key),
            entities.Provider: ThingContainer(generate_key_func=generate_key)
        }

    def get_all_entities(self, entities_type: Union[entities.Entity, list[entities.Entity, None]]):
        if not entities_type:
            entities_ = []
            for entity_type, container in self.entities_containers.items():
                typed_entities = container.get_all_things()
                entities_.extend(typed_entities)
            return entities_
        if isinstance(entities_type, list):
            entities_ = []
            for type_ in entities_type:
                entities_.extend(self.get_all_entities(entities_type=type_))
                container = self.entities_containers[type_]
                entities_.extend(container.get_all_things())
        else:
            container = self.entities_containers[entities_type]
            entities_ = container.get_all_things()
        return entities_

    def add_entity(self, entity: entities.Entity, **kwargs):
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
        key = generate_key(entity_type=entity_type, **kwargs)
        return key in self.entities_containers





