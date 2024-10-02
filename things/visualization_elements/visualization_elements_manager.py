import logging

from things.thing_container import ThingContainer
from . import visualization_elements
from .visualization_elements import CityScatter, CityTextBox


class CityScatterAndText:

    def __init__(self, city_scatter=None, city_text_box=None, city_name=None, **kwargs):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box
        self.city_name = city_name

        if self.city_scatter is None or self.city_text_box is None:
            raise ValueError("Both 'CityScatter' and 'CityTextBox' instances are required.")


def _is_scatter_and_text(visualization_elements: list):
    if len(visualization_elements) != 2:
        return
    return (isinstance(visualization_elements[0], visualization_elements.CityScatter) and isinstance(visualization_elements[1], CityTextBox)) or \
        (isinstance(visualization_elements[0], visualization_elements.CityTextBox) and isinstance(visualization_elements[1], CityScatter))


def _generate_key(element_type, **kwargs):
    if element_type is visualization_elements.Line:
        key = visualization_elements.Line, kwargs['origin_city'], kwargs['visiting_city']
    elif element_type is visualization_elements.CityScatter:
        key = visualization_elements.CityScatter, kwargs['city_name']
    elif element_type is visualization_elements.CityTextBox:
        key = visualization_elements.CityTextBox, kwargs['city_name']
    elif element_type is CityScatterAndText:
        key = CityScatterAndText, kwargs['city_name']
    else:
        raise TypeError(f"Could not create key for element type {element_type}")
    logging.info(f"Generated key: {key}")
    return key


class VisualizationElementsManager:

    def __init__(self):
        self.vis_element_containers = {
            visualization_elements.Line: ThingContainer(visualization_elements.Line, _generate_key),
            visualization_elements.CityScatter: ThingContainer(visualization_elements.CityScatter, _generate_key),
            visualization_elements.CityTextBox: ThingContainer(visualization_elements.CityTextBox, _generate_key)
        }

        self.city_scatter_and_texts = {}

    def add_city_scatter_and_text(self, city_scatter_and_text: CityScatterAndText):
        key = _generate_key(type(city_scatter_and_text), city_name=city_scatter_and_text.city_name)
        self.city_scatter_and_texts[key] = city_scatter_and_text

    def add_visualization_elements(self, visualization_elements: list[visualization_elements.VisualizationElement]):
        for vis_element in visualization_elements:
            container = self.vis_element_containers[type(vis_element)]
            container.add_thing(thing=vis_element)

    def get_all(self, visualization_element_types):
        vis_elements = set()
        for vis_ele_type in visualization_element_types:
            vis_eles_container = self.vis_element_containers[vis_ele_type]
            vis_elements.update(vis_eles_container.get_all_things())
        return vis_elements

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
