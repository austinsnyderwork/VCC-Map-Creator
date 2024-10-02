import logging
from typing import Callable

from things import entities
import config_manager
import environment_management
from .visualization_elements import visualization_elements


def _get_setting(variable: str, default, **kwargs):
    if variable in kwargs.items():
        return kwargs[variable]
    else:
        return default


def convert_visualization_element(vis_element: visualization_elements.VisualizationElement, desired_type):
    new_data = {}
    vis_element_is_dual_vis_element = issubclass(desired_type, visualization_elements.DualVisualizationElement)
    algo_data_substring = 'algorithm_' if vis_element_is_dual_vis_element else ''
    map_data_substring = 'map_' if vis_element_is_dual_vis_element else ''
    for k, v in vis_element.__dict__.items():
        new_data[k] = v
    if vis_element_is_dual_vis_element:
        for k, v in vis_element.algorithm_data.__dict__.items():
            new_data[f"{algo_data_substring}{k}"] = v
        for k, v in vis_element.map_data.__dict__.items():
            new_data[f"{map_data_substring}{k}"] = v
    new_vis_element = desired_type(**new_data)
    return new_vis_element


class DataConvertMap:

    def __init__(self, config, city_origin_network_handler):
        self.config = config
        self._scatter_marker_map = {
            'dual_origin_visiting': self.config.get_config_value('map_display.dual_origin_visiting_marker', str),
            'origin': self.config.get_config_value('map_display.origin_marker', str),
            'visiting': self.config.get_config_value('map_display.visiting_marker', str)
        }

        self._scatter_color_map = {
            'map': {
                'dual_origin_visiting': self.config.get_config_value('map_display.dual_origin_visiting_color', str),
                'origin': self.config.get_config_value('map_display.origin_color', str),
                'visiting': self.config.get_config_value('map_display.visiting_color', str)
            },
            'algorithm': {
                'dual_origin_visiting': self.config.get_config_value('algo_display.scatter_color', str),
                'origin': self.config.get_config_value('algo_display.scatter_color', str),
                'visiting': self.config.get_config_value('algo_display.scatter_color', str)
            }
        }

        self._line_color_map = {
            'map': city_origin_network_handler.get_entity_color,
            'algorithm': self.config.get_config_value('algo_display.line_color', str)
        }

        self._entity_to_vis_element_variables_conversion = {
            visualization_elements.CityScatter: {
                'name': 'city_name',
                'coord': 'algorithm_coord'
            },
            visualization_elements.CityTextBox: {
                'name': 'city_name',
                'coord': 'algorithm_coord'
            }
        }

        self._vis_element_algo_configs = {
            visualization_elements.CityScatter: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_scatter', bool)
            },
            visualization_elements.Line: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_line', bool)
            },
            visualization_elements.CityTextBox: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_scan_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_scan_poly', bool)
            },
            visualization_elements.TextBoxScanArea: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_scan_area_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_scan_area_poly', bool)
            },
            visualization_elements.Intersection: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_intersecting_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_intersecting_poly', bool)
            },
            visualization_elements.Best: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_best_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_best_poly', bool)
            },
            visualization_elements.TextBoxFinalist: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_poly_finalist', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_poly_finalist', bool)
            },
            visualization_elements.TextBoxNearbySearchArea: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_nearby_search_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_nearby_search_poly', bool)
            }
        }

    def get_scatter_marker(self, site_type: str):
        return self._scatter_marker_map[site_type]

    def get_scatter_color(self, site_type: str, display_type: str):
        return self._scatter_color_map[display_type][site_type]

    def get_line_color(self, entity: entities.Entity, display_type: str) -> str:
        if display_type == 'map':
            color_output = self._line_color_map[display_type](entity)
        else:
            color_output = self._line_color_map[display_type]
        return color_output

    def get_variable_conversions(self, entity_type):
        if entity_type in self._entity_to_vis_element_variables_conversion:
            return self._entity_to_vis_element_variables_conversion[entity_type]
        else:
            return {}
        
    def get_algorithm_config_data(self, visualization_element: visualization_elements.VisualizationElement):
        return self._vis_element_algo_configs[type(visualization_element)]


class ThingConverter:

    def __init__(self, config: config_manager.ConfigManager,
                 entities_manager: entities.EntitiesManager,
                 city_origin_network_handler: environment_management.CityOriginNetworkHandler,
                 get_text_display_dimensions: Callable):
        self.config = config
        self.entities_manager = entities_manager
        self.get_text_display_dimensions_func = get_text_display_dimensions

        self.data_converter_map = DataConvertMap(config=config,
                                                 city_origin_network_handler=city_origin_network_handler)

        self.entity_to_vis_element_map = {
            entities.City: [visualization_elements.CityScatter, visualization_elements.CityTextBox],
            entities.ProviderAssignment: visualization_elements.Line
        }

        self.vis_element_data_func_map = {
            visualization_elements.CityScatter: self._produce_city_scatter_data,
            visualization_elements.CityTextBox: self._produce_city_text_box_data,
            visualization_elements.Line: self._produce_line_data
        }

        self.provider_assignments_data_agg = {}

    def fill_in_data(self, visualization_element: visualization_elements.VisualizationElement, entity: entities.Entity,
                     **kwargs):
        entity_to_vis_ele_variables = self.data_converter_map.get_variable_conversions(type(visualization_element))
        for entity_variable, visualization_variable in entity_to_vis_ele_variables.items():
            new_value = getattr(entity, entity_variable)
            setattr(visualization_element, visualization_variable, new_value)

        vis_element_data_func = self.vis_element_data_func_map[type(visualization_element)]
        vis_element_data = vis_element_data_func(entity, **kwargs)
        for key, value in vis_element_data.items():
            if not hasattr(visualization_element, key) or getattr(visualization_element, key) is None:
                setattr(visualization_element, key, value)
                
        vis_element_algo_configs = self.data_converter_map.get_algorithm_config_data(visualization_element=visualization_element)
        for key, value in vis_element_algo_configs.items():
            if not hasattr(visualization_element, key) or getattr(visualization_element, key) is None:
                setattr(visualization_element, key, value)

    def _produce_city_scatter_data(self, city_entity: entities.City, **kwargs):
        city_type = city_entity.site_type
        scatter_data = {
            'city_name': city_entity.name,
            'site_type': city_entity.site_type,
            'map_color': _get_setting(variable='color',
                                      default=self.data_converter_map.get_scatter_color(city_type,
                                                                                        display_type='map'),
                                      kwargs=kwargs),
            'algorithm_color': _get_setting(variable='color',
                                            default=self.data_converter_map.get_scatter_color(city_type,
                                                                                              display_type='algorithm'),
                                            kwargs=kwargs),
            'map_edgecolor': _get_setting(variable='edgecolor',
                                          default=self.data_converter_map.get_scatter_color(city_type,
                                                                                            display_type='map'),
                                          kwargs=kwargs),
            'algorithm_edgecolor': _get_setting(variable='edgecolor',
                                                default=self.data_converter_map.get_scatter_color(city_type,
                                                                                                  display_type='algorithm'),
                                                kwargs=kwargs),
            'map_marker': _get_setting(variable='marker',
                                       default=self.data_converter_map.get_scatter_marker(city_type),
                                       kwargs=kwargs),
            'map_size': _get_setting(variable='size',
                                     default=self.config.get_config_value(key='map_display.scatter_size',
                                                                          cast_type=int),
                                     kwargs=kwargs),
            'map_label': _get_setting(variable='label',
                                      default=city_entity.site_type,
                                      kwargs=kwargs),
            'algorithm_coord': _get_setting(variable='coord',
                                            default=city_entity.coord,
                                            kwargs=kwargs),
            'algorithm_transparency': _get_setting(variable='transparency',
                                                   default=self.config.get_config_value(
                                                       key='algo_display.scatter_transparency',
                                                       cast_type=float))
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
        text_box_data['site_type'] = city_entity.site_type
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

        map_color = self.data_converter_map.get_line_color(entity=assignment_entity,
                                                           display_type='map')
        algorithm_color = self.data_converter_map.get_line_color(entity=assignment_entity,
                                                                 display_type='algorithm')
        line_data = {
            'origin_city': assignment_entity.origin_city_name,
            'visiting_city': assignment_entity.visiting_city_name,
            'origin_site': assignment_entity.origin_site_name,
            'visiting_site': assignment_entity.visiting_site_name,
            'algorithm_x_data': x_data,
            'algorithm_y_data': y_data,
            'map_linewidth': self.config.get_config_value(key='map_display.linewidth', cast_type=int),
            'algorithm_transparency': self.config.get_config_value(key='algo_display.line_transparency', cast_type=float),
            'map_color': map_color,
            'map_edgecolor': map_color,
            'algorithm_color': algorithm_color,
            'algorithm_edgecolor': algorithm_color
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
