import entities


def _generate_key(entity_type, **kwargs):
    if entity_type is entities.Line:
        return 'line', kwargs['origin'], kwargs['outpatient']
    elif entity_type is entities.CityScatter:
        return 'city_scatter', kwargs['city_name']
    elif entity_type is entities.CityTextBox:
        return 'city_text_box', kwargs['city_name']


class EntitiesManager:

    def __init__(self):
        self.entities = {}

    def add_entity(self, entity):
        key = _generate_key(entity_type=type(entity),
                            kwargs=entity.__dict__)
        self.entities[key] = entity

    def retrieve_entity(self, entity_type, **kwargs):
        key = _generate_key(entity_type=entity_type,
                            **kwargs)
        return self.entities[key]
