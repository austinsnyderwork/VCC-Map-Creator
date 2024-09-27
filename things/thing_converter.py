from typing import Callable

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

    def _produce_city_scatter_data(self, city_entity: entities.City):
        city_type = city_entity.site_type
        scatter_data = {
            'color': self.scatter_color_map[city_type],
            'edgecolor': self.scatter_color_map[city_type],
            'marker': self.scatter_marker_map[city_entity.site_type],
            'size': self.config.get_config_value(key='map_display.scatter_size', cast_type=int),
            'label': city_entity.site_type
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
        origin_city = self.entities_manager.get_city(name=assignment_entity.origin_site_name)
        visiting_city = self.entities_manager.get_city(name=assignment_entity.visiting_site_name)


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

    def convert_thing(self, entity: entities.Entity):
        if type(entity) is entities.ProviderAssignment:
            line_data = self._produce_provider_assignment_line_data(entity)
            line = visualization_elements.Line(**line_data)
            return line
        elif type(entity) is entities.City:
            scatter_data = self._produce_city_scatter_data(entity)
            city_scatter = visualization_elements.CityScatter(**scatter_data)

            text_box_data = self._produce_city_text_box_data(city_entity=entity)
            text_box = visualization_elements.CityTextBox(**text_box_data)

            city_scatter_and_text = visualization_elements.CityScatterAndText(city_scatter=city_scatter,
                                                                              city_text_box=text_box)

            return city_scatter_and_text
