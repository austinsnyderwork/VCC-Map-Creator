import logging

import config_manager
from things.visualization_elements import visualization_elements


class MapDisplayController:

    def __init__(self,
                 show_origin_scatters=True,
                 show_visiting_scatters=True,
                 show_dual_text_box=True,
                 show_origin_text_box=True,
                 show_visiting_text_box=True,
                 show_dual_scatters=True,
                 show_line=True):
        self.master_display_origin_visiting_settings = {
            visualization_elements.CityScatter: {
                'origin': show_origin_scatters,
                'visiting': show_visiting_scatters,
                'dual_origin_visiting': show_dual_scatters
            },
            visualization_elements.CityTextBox: {
                'origin': show_origin_text_box,
                'visiting': show_visiting_text_box,
                'dual_origin_visiting': show_dual_text_box
            }
        }

        self.master_display_settings = {
            visualization_elements.Line: show_line
        }

    def should_display(self, vis_element=None, vis_element_type=None, site_type=None, *args, **kwargs):
        if vis_element:
            if hasattr(vis_element, 'site_type'):
                site_type = getattr(vis_element, 'site_type')
            vis_element_type = type(vis_element)

        if vis_element_type in self.master_display_origin_visiting_settings:
            return self.master_display_origin_visiting_settings[vis_element_type][vis_element][site_type]
        elif type(vis_element) is visualization_elements.Line:
            return self.master_display_settings[visualization_elements.Line]
        else:
            raise TypeError(f"Vis ele type {type(vis_element)} is not accepted.")


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

        self.visualization_elements_display = {
            visualization_elements.Line: self.retrieve_setting('algo_display_show_line', True),
            visualization_elements.CityTextBox: self.retrieve_setting('algo_display_show_scan_poly', True),
            visualization_elements.TextBoxScanArea: self.retrieve_setting('algo_display_show_search_area_poly', True),
            visualization_elements.TextBoxFinalist: self.retrieve_setting('algo_display_show_poly_finalist', True),
            visualization_elements.TextBoxNearbySearchArea: self.retrieve_setting('algo_display_show_nearby_search_poly', True),
            visualization_elements.Intersection: self.retrieve_setting('algo_display_show_intersecting_poly', True)
        }

        self.visualization_time_iterations_display = {
            visualization_elements.CityTextBox: self.retrieve_setting('algo_display_steps_to_show_scan_poly', True),
            visualization_elements.TextBoxScanArea: self.retrieve_setting('algo_display_steps_to_show_scan_poly', True),
            visualization_elements.TextBoxFinalist: self.retrieve_setting('algo_display_steps_to_show_poly_finalist', True),
            visualization_elements.TextBoxNearbySearchArea: self.retrieve_setting('algo_display_steps_to_show_poly_finalist', True)
        }

    def should_display(self, visualization_element, iterations: int = None) -> bool:
        show_algo = self.retrieve_setting('algo_display_show_algo', bool)
        if not show_algo:
            return False

        visualization_element_type = type(visualization_element)
        if visualization_element_type in self.entity_type_display_origin_visiting:
            if not self.entity_type_display_origin_visiting[visualization_element_type][visualization_element.site_type]:
                return False

        if visualization_element_type in self.visualization_elements_display:
            if not self.visualization_elements_display[visualization_element_type]:
                return False

        if visualization_element_type in self.visualization_time_iterations_display:
            if iterations and iterations != self.visualization_time_iterations_display[visualization_element_type]:
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
                 show_origin_scatters=True,
                 show_visiting_scatters=True,
                 show_dual_text_box=True,
                 show_origin_text_box=True,
                 show_visiting_text_box=True,
                 show_dual_scatters=True,
                 show_line=True,
                 show_scan_poly=True,
                 show_search_area_poly=True,
                 show_poly_finalist=True,
                 show_nearby_search_poly=True,
                 show_intersecting_poly=True,
                 **plot_settings):
        self.map_display_controller = MapDisplayController(**plot_settings)
        self.algorithm_display_controller = AlgorithmDisplayController(**plot_settings)
        self.config = config if config else config_manager.ConfigManager()
        self.plot_settings = plot_settings

        self.master_display_origin_visiting_settings = {
            visualization_elements.CityScatter: {
                'origin': show_origin_scatters,
                'visiting': show_visiting_scatters,
                'dual_origin_visiting': show_dual_scatters
            },
            visualization_elements.CityTextBox: {
                'origin': show_origin_text_box,
                'visiting': show_visiting_text_box,
                'dual_origin_visiting': show_dual_text_box
            }
        }

        self.master_display_settings = {
            visualization_elements.Line: show_line,
            visualization_elements.CityTextBox: show_scan_poly,
            visualization_elements.TextBoxScanArea: show_search_area_poly,
            visualization_elements.TextBoxFinalist: show_poly_finalist,
            visualization_elements.TextBoxNearbySearchArea: show_nearby_search_poly,
            visualization_elements.Intersection: show_intersecting_poly
        }

    def should_display(self, visualization_element: visualization_elements.VisualizationElement, display_type: str,
                       iterations: int = None, **kwargs) -> bool:
        visualization_element_type = type(visualization_element)

        should_display_funcs = {
            'map': self.map_display_controller.should_display,
            'algorithm': self.algorithm_display_controller.should_display
        }
        return should_display_funcs[display_type](visualization_element_type, iterations)



