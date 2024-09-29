from typing import Callable, Union

from things import entities
import config_manager
import environment_management
from .visualization_elements import visualization_elements


class ThingConverter:

    def __init__(self, config: config_manager.ConfigManager,
                 entities_manager: entities.EntitiesManager,
                 city_origin_network_handler: environment_management.CityOriginNetworkHandler,
                 get_text_display_dimensions: Callable):
        self.config = config
        self.entities_manager = entities_manager
        self.city_origin_network_handler = city_origin_network_handler

        self.get_text_display_dimensions_func = get_text_display_dimensions

        self.entity_to_vis_element_map = {
            entities.City: [visualization_elements.CityScatter, visualization_elements.CityTextBox],
            entities.ProviderAssignment: visualization_elements.Line
        }

        self.scatter_marker_map = {
            'dual_origin_visiting': self.config.get_config_value('map_display.dual_origin_visiting_marker', str),
            'origin': self.config.get_config_value('map_display.origin_marker', str),
            'visiting': self.config.get_config_value('map_display.visiting_marker', str)
        }

        self.scatter_color_map = {
            'dual_origin_visiting': self.config.get_config_value('map_display.dual_origin_visiting_color', str),
            'origin': self.config.get_config_value('map_display.origin_color', str),
            'visiting': self.config.get_config_value('map_display.visiting_color', str)
        }

    def fill_in_data(self, entity: entities.Entity, visualization_element: visualization_elements.VisualizationElement):
        data_variables = {
            visualization_elements.CityScatter: {
                'name': 'city_name',
                'coord': 'algorithm_coord'
            },
            visualization_elements.CityTextBox: {
                'name': 'city_name',
                'coord': 'algorithm_coord'
            }
        }
        if type(visualization_element) in data_variables:
            variables_dict = data_variables[type(visualization_element)]
            for entity_name, visualization_name in variables_dict.items():
                new_value = getattr(entity, entity_name)
                setattr(visualization_element, visualization_name, new_value)

    def _produce_city_scatter_data(self, city_entity: entities.City):
        city_type = city_entity.site_type
        scatter_data = {
            'color': self.scatter_color_map[city_type],
            'edgecolor': self.scatter_color_map[city_type],
            'marker': self.scatter_marker_map[city_entity.site_type],
            'size': self.config.get_config_value(key='map_display.scatter_size', cast_type=int),
            'label': city_entity.site_type,
            'coord': city_entity.coord
        }
        return scatter_data

    def _produce_city_text_box_data(self, city_entity: entities.City):
        font_size = self.config.get_config_value('map_display.city_font_size', int)
        font_weight = self.config.get_config_value('map_display.city_font_weight', str)
        font = self.config.get_config_value('map_display.city_font', str)
        text_box_data = self.get_text_display_dimensions_func(city_entity,
                                                              font_size=font_size,
                                                              font_weight=font_weight,
                                                              font=font)
        return text_box_data

    def _produce_provider_assignment_line_data(self, assignment_entity: entities.ProviderAssignment):
        origin_city = self.entities_manager.get_city(name=assignment_entity.origin_city_name)
        visiting_city = self.entities_manager.get_city(name=assignment_entity.visiting_city_name)

        x_data = origin_city.coord[0], visiting_city.coord[0]
        y_data = origin_city.coord[1], visiting_city.coord[1]

        color = self.city_origin_network_handler.get_entity_color(entity=assignment_entity)
        line_data = {
            'x_data': x_data,
            'y_data': y_data,
            'linewidth': self.config.get_config_value(key='map_display.linewidth', cast_type=int),
            'color': color,
            'edgecolor': color
        }
        return line_data

    def convert_thing(self, entity: entities.Entity) -> list[visualization_elements.VisualizationElement]:
        if type(entity) is entities.ProviderAssignment:
            entity: entities.ProviderAssignment
            line_data = self._produce_provider_assignment_line_data(entity)
            line = visualization_elements.Line(**line_data)
            vis_elements = [line]
        elif type(entity) is entities.City:
            entity: entities.City
            scatter_data = self._produce_city_scatter_data(entity)
            city_scatter = visualization_elements.CityScatter(**scatter_data)

            text_box_data = self._produce_city_text_box_data(city_entity=entity)
            text_box = visualization_elements.CityTextBox(city_name=entity.name,
                                                          **text_box_data)
            vis_elements = [city_scatter, text_box]
        else:
            raise RuntimeError("Unable to convert thing.")

        return vis_elements

    def convert_entities_to_visualization_elements(self, entities_: list[entities.Entity]) -> list[visualization_elements.VisualizationElement]:
        vis_elements = []
        for entity in entities_:
            visualization_element = self.convert_thing(entity)
            vis_elements.append(visualization_element)
        return vis_elements
