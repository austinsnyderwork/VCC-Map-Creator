

from things.thing_container import ThingContainer
import visualization_elements


def _generate_key(element_type, **kwargs):
    if element_type is visualization_elements.Line:
        return visualization_elements.Line, kwargs['origin'], kwargs['visiting']
    elif element_type is visualization_elements.CityScatter:
        return visualization_elements.CityScatter, kwargs['city_name']
    elif element_type is visualization_elements.CityTextBox:
        return visualization_elements.CityTextBox, kwargs['city_name']


class VisualizationElementsManager:

    def __init__(self):
        self.vis_element_containers = {
            visualization_elements.Line: ThingContainer(_generate_key),
            visualization_elements.CityScatter: ThingContainer(_generate_key),
            visualization_elements.CityTextBox: ThingContainer(_generate_key)
        }

    def add_element(self, element):
        container = self.vis_element_containers[type(element)]
        container.add_thing(thing=element)

    def get_line(self, origin_city_name: str, visiting_city_name: str):
        container = self.vis_element_containers[visualization_elements.Line]
        vis_element = container.get_thing(thing_type=visualization_elements.Line,
                                          origin_city_name=origin_city_name,
                                          visiting_city_name=visiting_city_name)
        return vis_element

    def get_city_scatter(self, city_name: str):
        container = self.vis_element_containers[visualization_elements.CityScatter]
        vis_element = container.get_thing(thing_type=visualization_elements.CityScatter,
                                          city_name=city_name)
        return vis_element

    def get_city_text_box(self, city_name: str):
        container = self.vis_element_containers[visualization_elements.CityTextBox]
        vis_element = container.get_thing(thing_type=visualization_elements.CityTextBox,
                                          city_name=city_name)
        return vis_element
