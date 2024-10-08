import logging

from things.thing_container import ThingContainer
from .visualization_element_filler import VisualizationElementFiller
from .vis_element_classes import CityScatter, Best, Line


class CityScatterAndText:

    def __init__(self, city_scatter=None, city_text_box=None, city_name=None, **kwargs):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box
        self.city_name = city_name

        if self.city_scatter is None or self.city_text_box is None:
            raise ValueError("Both 'CityScatter' and 'CityTextBox' instances are required.")


def _generate_key(element_type, **kwargs):
    if element_type is Line:
        key = Line, kwargs['origin_city'], kwargs['visiting_city']
    elif element_type is CityScatter:
        key = CityScatter, kwargs['city_name']
    elif element_type is Best:
        key = Best, kwargs['city_name']
    elif element_type is CityScatterAndText:
        key = CityScatterAndText, kwargs['city_name']
    else:
        raise TypeError(f"Could not create key for element type {element_type}")
    logging.info(f"Generated key: {key}")
    return key


class VisualizationElementsManager:

    def __init__(self, config):
        self.vis_element_containers = {
            Line: ThingContainer(Line, _generate_key),
            CityScatter: ThingContainer(CityScatter, _generate_key),
            Best: ThingContainer(Best, _generate_key)
        }

        self.vis_element_filler = VisualizationElementFiller(config=config)

        self.polygon_to_vis_element = {}

        self.city_scatter_and_texts = {}

    def add_city_scatter_and_text(self, city_scatter_and_text: CityScatterAndText):
        key = _generate_key(type(city_scatter_and_text), city_name=city_scatter_and_text.city_name)
        self.city_scatter_and_texts[key] = city_scatter_and_text

    def add_visualization_elements(self, visualization_elements_: list):
        for vis_element in visualization_elements_:
            if type(vis_element) not in self.vis_element_containers.keys():
                continue
            if hasattr(vis_element, 'default_poly'):
                self.polygon_to_vis_element[vis_element.default_poly] = vis_element
            container = self.vis_element_containers[type(vis_element)]
            container.add_thing(thing=vis_element)

    def get_vis_element(self, polygon):
        return self.polygon_to_vis_element[polygon]

    def get_all(self, visualization_element_types):
        vis_elements = set()
        for vis_ele_type in visualization_element_types:
            vis_eles_container = self.vis_element_containers[vis_ele_type]
            vis_elements.update(vis_eles_container.get_all_things())
        return vis_elements

    def fill_element(self, vis_element):
        return self.vis_element_filler.fill_element(vis_element)
