import logging

import config_manager
from things.visualization_elements import visualization_elements


class MapDisplayController:

    def __init__(self, **plot_settings):
        self.config = config_manager.ConfigManager()
        self.plot_settings = plot_settings

        self.entity_type_display = {
            visualization_elements.Line: self.retrieve_setting('map_display_show_line', True),
            visualization_elements.TextBoxScan: self.retrieve_setting('map_display_show_scan_poly', True),
            visualization_elements.TextBoxScanArea: self.retrieve_setting('map_display_show_scan_area_poly', True),
            visualization_elements.CityScatter: self.retrieve_setting('map_display_show_scatter', True),
            visualization_elements.Intersection: self.retrieve_setting('map_display_show_intersecting_poly', True),
            visualization_elements.TextBoxFinalist: self.retrieve_setting('map_display_show_finalist_poly', True),
            visualization_elements.TextBoxNearbySearchArea: self.retrieve_setting('map_display_show_nearby_search_poly', True),
        }

    def should_display(self, entity_type, *args, **kwargs) -> bool:
        return self.entity_type_display[entity_type]

    def retrieve_setting(self, key, default_value):
        if key in self.plot_settings:
            return self.plot_settings[key]

        try:
            return self.config.get_config_value(key, type(default_value))
        except KeyError:
            return default_value


class AlgorithmDisplayController:

    def __init__(self, **plot_settings):
        self.config = config_manager.ConfigManager()
        self.plot_settings = plot_settings

        self.entity_type_display_origin_visiting = {
            visualization_elements.CityScatter: {
                'origin': self.retrieve_setting('algo_display_show_origin_scatters', True),
                'visiting': self.retrieve_setting('algo_display_show_origin_visitings', True)
            },
            visualization_elements.CityTextBox: {
                'origin': self.retrieve_setting('algo_display_show_origin_text_box', True),
                'visiting': self.retrieve_setting('algo_display_show_visiting_text_box', True)
            }
        }

        self.entities_display = {
            visualization_elements.Line: self.retrieve_setting('algo_display_show_line', True),
            visualization_elements.TextBoxScan: self.retrieve_setting('algo_display_show_scan_poly', True),
            visualization_elements.TextBoxScanArea: self.retrieve_setting('algo_display_show_search_area_poly', True),
            visualization_elements.TextBoxFinalist: self.retrieve_setting('algo_display_show_poly_finalist', True),
            visualization_elements.TextBoxNearbySearchArea: self.retrieve_setting('algo_display_show_nearby_search_poly', True),
            visualization_elements.Intersection: self.retrieve_setting('algo_display_show_intersecting_poly', True)
        }

        self.entity_type_iterations_display = {
            visualization_elements.TextBoxScan: self.retrieve_setting('algo_display_steps_to_show_scan_poly', True),
            visualization_elements.TextBoxScanArea: self.retrieve_setting('algo_display_steps_to_show_scan_poly', True),
            visualization_elements.TextBoxFinalist: self.retrieve_setting('algo_display_steps_to_show_poly_finalist', True),
            visualization_elements.TextBoxNearbySearchArea: self.retrieve_setting('algo_display_steps_to_show_poly_finalist', True)
        }

    def should_display(self, entity_type, iterations: int = None) -> bool:
        show_algo = self.retrieve_setting('algo_display_show_algo', bool)
        if not show_algo:
            return False

        if entity_type in self.entity_type_display_origin_visiting:
            if not self.entity_type_display_origin_visiting[entity_type][entity_type.site_type]:
                return False

        if entity_type in self.entities_display:
            if not self.entities_display[entity_type]:
                return False

        if entity_type in self.entity_type_iterations_display:
            if iterations and iterations != self.entity_type_iterations_display[entity_type]:
                return False

        return True

    def retrieve_setting(self, key, default_value):
        if key in self.plot_settings:
            return self.plot_settings[key]

        try:
            return self.config.get_config_value(key, type(default_value))
        except KeyError:
            return default_value


class PlotController:

    def __init__(self,
                 config: config_manager.ConfigManager = None,
                 **plot_settings):
        self.map_display_controller = MapDisplayController(**plot_settings)
        self.algorithm_display_controller = AlgorithmDisplayController(**plot_settings)
        self.config = config if config else config_manager.ConfigManager()
        self.plot_settings = plot_settings

        self.master_display_origin_visiting_settings = {
            visualization_elements.CityScatter: {
                'origin': self.retrieve_setting('show_origin_scatters', True),
                'visiting': self.retrieve_setting('show_visiting_scatters', True),
                'dual_origin_visiting': self.retrieve_setting('show_dual_scatters', True)
            },
            visualization_elements.CityTextBox: {
                'origin': self.retrieve_setting('show_origin_text_box', True),
                'visiting': self.retrieve_setting('show_visiting_text_box', True),
                'dual_origin_visiting': self.retrieve_setting('show_dual_text_box', True)
            }
        }

        self.master_display_settings = {
            visualization_elements.Line: self.retrieve_setting('show_line', True),
            visualization_elements.TextBoxScan: self.retrieve_setting('show_scan_poly', True),
            visualization_elements.TextBoxScanArea: self.retrieve_setting('show_search_area_poly', True),
            visualization_elements.TextBoxFinalist: self.retrieve_setting('show_poly_finalist', True),
            visualization_elements.TextBoxNearbySearchArea: self.retrieve_setting('show_nearby_search_poly', True),
            visualization_elements.Intersection: self.retrieve_setting('show_intersecting_poly', True)
        }

    def retrieve_setting(self, key, default_value):
        if key in self.plot_settings:
            return self.plot_settings[key]

        try:
            return self.config.get_config_value(key, type(default_value))
        except KeyError:
            return default_value

    def should_display(self, visualization_element: visualization_elements.VisualizationElement, display_type: str,
                       iterations: int = None, **kwargs) -> bool:
        visualization_element_type = type(visualization_element)
        # If a master setting says don't display for this entity type, then immediately return False
        if visualization_element_type in self.master_display_origin_visiting_settings:
            if not self.master_display_origin_visiting_settings[visualization_element_type][visualization_element.site_type]:
                return False

        if type(visualization_element) in self.master_display_settings:
            if not self.master_display_settings[visualization_element_type]:
                return False

        should_display_funcs = {
            'map': self.map_display_controller.should_display,
            'algorithm': self.algorithm_display_controller.should_display
        }
        if not should_display_funcs[display_type](visualization_element_type, iterations):
            return False

        return True




