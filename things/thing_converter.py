from typing import Callable, Union

from things import entities
import config_manager
import environment_management
from .visualization_elements import visualization_elements


def _get_setting(variable: str, default, **kwargs):
    if variable in kwargs.items():
        return kwargs[variable]
    else:
        return default


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

        self.vis_element_data_func_map = {
            visualization_elements.CityScatter: self._produce_city_scatter_data,
            visualization_elements.CityTextBox: self._produce_city_text_box_data,
            visualization_elements.Line: self._produce_line_data
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

        self.provider_assignments_data_agg = {

        }

    def fill_in_data(self, visualization_element: visualization_elements.VisualizationElement, entity: entities.Entity,
                     **kwargs):
        entity_to_vis_element_data_variables = {
            visualization_elements.CityScatter: {
                'name': 'city_name',
                'coord': 'algorithm_coord'
            },
            visualization_elements.CityTextBox: {
                'name': 'city_name',
                'coord': 'algorithm_coord'
            }
        }
        if entity and type(visualization_element) in entity_to_vis_element_data_variables:
            variables_dict = entity_to_vis_element_data_variables[type(visualization_element)]
            for entity_name, visualization_name in variables_dict.items():
                new_value = getattr(entity, entity_name)
                setattr(visualization_element, visualization_name, new_value)

        vis_element_data = self.vis_element_data_func_map[type(visualization_element)](entity, **kwargs)
        for key, value in vis_element_data.items():
            if not hasattr(visualization_element, key) or getattr(visualization_element, key) is None:
                setattr(visualization_element, key, value)

    def _produce_city_scatter_data(self, city_entity: entities.City, **kwargs):
        city_type = city_entity.site_type
        scatter_data = {
            'color': _get_setting(variable='color',
                                  default=self.scatter_color_map[city_type],
                                  kwargs=kwargs),
            'edgecolor': _get_setting(variable='edgecolor',
                                      default=self.scatter_color_map[city_type],
                                      kwargs=kwargs),
            'marker': _get_setting(variable='marker',
                                   default=self.scatter_marker_map[city_entity.site_type],
                                   kwargs=kwargs),
            'size': _get_setting(variable='size',
                                 default=self.config.get_config_value(key='map_display.scatter_size', cast_type=int),
                                 kwargs=kwargs),
            'label': _get_setting(variable='label',
                                  default=city_entity.site_type,
                                  kwargs=kwargs),
            'coord': _get_setting(variable='coord',
                                  default=city_entity.coord,
                                  kwargs=kwargs)
        }
        return scatter_data

    def _produce_city_text_box_data(self, city_entity: entities.City, **kwargs):
        font_size = _get_setting(variable='fontsize',
                                 default=self.config.get_config_value('map_display.city_fontsize', int),
                                 kwargs=kwargs)
        font_weight = _get_setting(variable='fontweight',
                                   default=self.config.get_config_value('map_display.city_fontweight', str),
                                   kwargs=kwargs)
        font = _get_setting(variable='font',
                            default=self.config.get_config_value('map_display.city_font', str),
                            kwargs=kwargs)
        text_box_data = self.get_text_display_dimensions_func(city_entity,
                                                              font_size=font_size,
                                                              font_weight=font_weight,
                                                              font=font)
        text_box_data['map_fontsize'] = font_size
        text_box_data['map_fontweight'] = font_weight
        text_box_data['map_font'] = font
        return text_box_data

    def _produce_line_data(self, assignment_entity: entities.ProviderAssignment, **kwargs):
        origin_city = _get_setting(variable='origin_city',
                                   default=self.entities_manager.get_city(name=assignment_entity.origin_city_name),
                                   kwargs=kwargs)
        visiting_city = _get_setting(variable='visiting_city',
                                     default=self.entities_manager.get_city(name=assignment_entity.visiting_city_name),
                                     kwargs=kwargs)
        if frozenset([origin_city, visiting_city]) in self.provider_assignments_data_agg:
            line_data = self.provider_assignments_data_agg[frozenset([origin_city, visiting_city])]
            return line_data

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
        self.provider_assignments_data_agg[(frozenset([origin_city, visiting_city]))] = line_data
        return line_data

    def convert_thing(self, entity: entities.Entity) -> list[visualization_elements.VisualizationElement]:
        if type(entity) is entities.ProviderAssignment:
            entity: entities.ProviderAssignment
            line_data = self._produce_line_data(entity)
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

    def convert_entities_to_visualization_elements(self, entities_: list[entities.Entity]) -> list[
        visualization_elements.VisualizationElement]:
        vis_elements = []
        for entity in entities_:
            visualization_element = self.convert_thing(entity)
            vis_elements.append(visualization_element)
        return vis_elements
