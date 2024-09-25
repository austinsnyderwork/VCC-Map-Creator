import visualization_elements


def _generate_key(element_type, **kwargs):
    if element_type is visualization_elements.Line:
        return 'line', kwargs['origin'], kwargs['outpatient']
    elif element_type is visualization_elements.CityScatter:
        return 'city_scatter', kwargs['city_name']
    elif element_type is visualization_elements.CityTextBox:
        return 'city_text_box', kwargs['city_name']


class VisualizationElementsManager:

    def __init__(self):
        self.entities = {}

    def add_element(self, element):
        key = _generate_key(entity_type=type(element),
                            kwargs=element.__dict__)
        self.entities[key] = element

    def retrieve_element(self, element_type, **kwargs):
        key = _generate_key(entity_type=element_type,
                            **kwargs)
        return self.entities[key]
