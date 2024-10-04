from .vis_element_classes import (CityScatter, Line, CityTextBox, TextBoxNearbySearchArea, TextBoxScanArea,
                                  TextBoxFinalist, Best, Intersection)
from config_manager import ConfigManager


class VisualizationElementFiller:

    def __init__(self, config: ConfigManager):
        self.config = config
        self.string_by_element = {
            CityScatter: 'scatter',
            Line: 'line',
            CityTextBox: 'scan_poly',
            TextBoxNearbySearchArea: 'nearby_search_poly',
            TextBoxScanArea: 'scan_area',
            TextBoxFinalist: 'poly_finalist',
            Best: 'best_poly',
            Intersection: 'intersecting_poly'
        }

        self.zorder_elements = [CityScatter, Line, Best]

    def _get_config_values_by_element(self, vis_element):
        element_string = self.string_by_element[type(vis_element)]
        data = {
            'algorithm_show': self.config.get_config_value(f'algo_display.show_{element_string}', bool),
            'algorithm_color': self.config.get_config_value(f'algo_display.{element_string}_color', str),
            'algorithm_transparency': self.config.get_config_value(f'algo_display.{element_string}_transparency',
                                                                   float),
            'algorithm_immediately_remove': self.config.get_config_value(
                f'algo_display.immediately_remove_{element_string}', bool),
            'algorithm_center_view': self.config.get_config_value(f'algo_display.center_view_on_{element_string}', bool)
        }
        if type(vis_element) is CityScatter:
            data['map_color'] = self.config.get_config_value(f'map_display.{vis_element.site_type}_color', str)
            data['map_outer_color'] = self.config.get_config_value(f'map_display.{vis_element.site_type}_outer_color', str)
            data['map_marker'] = self.config.get_config_value(f'map_display.{vis_element.site_type}_marker', str)

        if type(vis_element) in self.zorder_elements:
            data['zorder'] = self.config.get_config_value(f'map_display.{element_string}_zorder', int)

        return data

    def fill_element(self, vis_element):
        data = self._get_config_values_by_element(vis_element)
        for k, v in data.items():
            if not hasattr(vis_element, k) or getattr(vis_element, k) is None:
                setattr(vis_element, k, v)
        return vis_element

