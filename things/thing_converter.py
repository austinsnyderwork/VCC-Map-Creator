import logging
from typing import Callable, Union

from things import entities
import config_manager
import environment_management
from .visualization_elements import CityScatterAndText, visualization_elements


def _get_setting(variable: str, default, **kwargs):
    if variable in kwargs.items():
        return kwargs[variable]
    else:
        return default


def _set_attr(obj, k, v):
    if not hasattr(obj, k) or getattr(obj, k) is None:
        setattr(obj, k, v)


def convert_visualization_element(vis_element: visualization_elements.VisualizationElement, desired_type=None,
                                  new_vis_element=None, **extra_vis_element_data):
    if new_vis_element:
        desired_type = type(new_vis_element)
    else:
        new_vis_element = desired_type()

    for k, v in extra_vis_element_data.items():
        _set_attr(new_vis_element, k, v)
    vis_element_is_dual_vis_element = issubclass(type(vis_element), visualization_elements.DualVisualizationElement)
    desired_type_is_dual_vis_element = issubclass(desired_type, visualization_elements.DualVisualizationElement)
    for k, v in vis_element.__dict__.items():
        if k in ('algorithm_data', 'map_data') and not desired_type_is_dual_vis_element:
            continue
        _set_attr(new_vis_element, k, v)
    if vis_element_is_dual_vis_element:
        if not desired_type_is_dual_vis_element:
            for k, v in vis_element.algorithm_data.__dict__.items():
                k = k.replace('algorithm_', '')
                _set_attr(new_vis_element, k, v)
            for k, v in vis_element.map_data.__dict__.items():
                k = k.replace('map_', '')
                _set_attr(new_vis_element, k, v)
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

        self._vis_element_algo_configs = {
            visualization_elements.CityScatter: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_scatter',
                                                                             bool)
            },
            visualization_elements.Line: {
                'algorithm_immediately_remove': self.config.get_config_value('algo_display.immediately_remove_line',
                                                                             bool)
            },
            visualization_elements.CityTextBox: {
                'algorithm_immediately_remove': self.config.get_config_value(
                    'algo_display.immediately_remove_scan_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_scan_poly', bool)
            },
            visualization_elements.TextBoxScanArea: {
                'algorithm_immediately_remove': self.config.get_config_value(
                    'algo_display.immediately_remove_scan_area_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_scan_area_poly',
                                                                      bool)
            },
            visualization_elements.Intersection: {
                'algorithm_immediately_remove': self.config.get_config_value(
                    'algo_display.immediately_remove_intersecting_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_intersecting_poly',
                                                                      bool)
            },
            visualization_elements.Best: {
                'algorithm_immediately_remove': self.config.get_config_value(
                    'algo_display.immediately_remove_best_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_best_poly', bool)
            },
            visualization_elements.TextBoxFinalist: {
                'algorithm_immediately_remove': self.config.get_config_value(
                    'algo_display.immediately_remove_poly_finalist', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_poly_finalist', bool)
            },
            visualization_elements.TextBoxNearbySearchArea: {
                'algorithm_immediately_remove': self.config.get_config_value(
                    'algo_display.immediately_remove_nearby_search_poly', bool),
                'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_nearby_search_poly',
                                                                      bool)
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

        self.variables_to_pull = {
            entities.City: ['city_coord', 'city_name'],
            entities.ProviderAssignment: ['origin_city_name', 'visiting_city_name']
        }

        self.provider_assignments_data_agg = {}

    def fill_in_data(self, visualization_element: visualization_elements.VisualizationElement, entity: entities.Entity,
                     **kwargs):
        variables_to_pull = self.variables_to_pull[type(entity)]
        for variable in variables_to_pull:
            setattr(visualization_element, variable, getattr(entity, variable))

        vis_element_data_func = self.vis_element_data_func_map[type(visualization_element)]
        vis_element_data = vis_element_data_func(entity, **kwargs)
        for key, value in vis_element_data.items():
            if not hasattr(visualization_element, key) or getattr(visualization_element, key) is None:
                setattr(visualization_element, key, value)

        vis_element_algo_configs = self.data_converter_map.get_algorithm_config_data(
            visualization_element=visualization_element)
        for key, value in vis_element_algo_configs.items():
            if not hasattr(visualization_element, key) or getattr(visualization_element, key) is None:
                setattr(visualization_element, key, value)

    def _produce_city_scatter_data(self, city_entity: entities.City, **kwargs):
        city_type = city_entity.site_type
        scatter_data = {
            'algorithm_show': _get_setting(variable='show',
                                           default=self.config.get_config_value('algo_display.show_scatter', bool),
                                           kwargs=kwargs),
            'algorithm_center_view': _get_setting(variable='center_view',
                                                  default=self.config.get_config_value(
                                                      'algo_display.center_view_on_scatter', bool),
                                                  kwargs=kwargs),
            'city_name': city_entity.city_name,
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
                                            default=city_entity.city_coord,
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
        if frozenset([assignment_entity.origin_city_name,
                      assignment_entity.visiting_city_name]) in self.provider_assignments_data_agg:
            line_data = self.provider_assignments_data_agg[
                frozenset([assignment_entity.origin_city_name, assignment_entity.visiting_city_name])]
            return line_data

        origin_city_obj = self.entities_manager.get_city(assignment_entity.origin_city_name)
        visiting_city_obj = self.entities_manager.get_city(assignment_entity.visiting_city_name)

        x_data = origin_city_obj.city_coord[0], visiting_city_obj.city_coord[0]
        y_data = origin_city_obj.city_coord[1], visiting_city_obj.city_coord[1]

        map_color = self.data_converter_map.get_line_color(entity=assignment_entity,
                                                           display_type='map')
        algorithm_color = self.data_converter_map.get_line_color(entity=assignment_entity,
                                                                 display_type='algorithm')
        line_data = {
            'algorithm_show': self.config.get_config_value('algo_display.show_line', bool),
            'origin_city': assignment_entity.origin_city_name,
            'visiting_city': assignment_entity.visiting_city_name,
            'origin_site': assignment_entity.origin_site_name,
            'visiting_site': assignment_entity.visiting_site_name,
            'x_data': x_data,
            'y_data': y_data,
            'map_linewidth': self.config.get_config_value('map_display.linewidth', int),
            'algorithm_transparency': self.config.get_config_value('algo_display.line_transparency', float),
            'map_color': map_color,
            'map_edgecolor': map_color,
            'algorithm_color': algorithm_color,
            'algorithm_edgecolor': algorithm_color,
            'algorithm_center_view': self.config.get_config_value('algo_display.center_view_on_line', bool)
        }
        self.provider_assignments_data_agg[(frozenset([assignment_entity.origin_city_name,
                                                       assignment_entity.visiting_city_name]))] = line_data
        return line_data

    def convert_thing(self, entity: entities.Entity) -> Union[visualization_elements.Line, CityScatterAndText]:
        if type(entity) is entities.ProviderAssignment:
            entity: entities.ProviderAssignment
            line_data = self._produce_line_data(entity)
            line = visualization_elements.Line(**line_data)
            return line
        elif type(entity) is entities.City:
            entity: entities.City
            scatter_data = self._produce_city_scatter_data(entity)
            city_scatter = visualization_elements.CityScatter(**scatter_data)

            text_box_data = self._produce_city_text_box_data(city_entity=entity)
            text_box = visualization_elements.CityTextBox(city_name=entity.city_name,
                                                          **text_box_data)
            city_scatter_and_text = CityScatterAndText(city_scatter=city_scatter,
                                                       city_text_box=text_box,
                                                       city_name=entity.city_name)
            return city_scatter_and_text
        else:
            raise RuntimeError("Unable to convert thing.")

    def convert_entities_to_visualization_elements(self, entities_: list[entities.Entity]) -> list[
        visualization_elements.VisualizationElement]:
        vis_elements = []
        for entity in entities_:
            visualization_element = self.convert_thing(entity)
            vis_elements.append(visualization_element)
        return vis_elements
