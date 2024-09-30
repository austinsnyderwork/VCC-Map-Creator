from typing import Union

import algorithm
import config_manager
from . import PlotController
from things.visualization_elements import visualization_elements
import map


class PlotManager:

    def __init__(self, algorithm_handler: algorithm.AlgorithmHandler,
                 map_plotter: map.MapPlotter, plot_controller: PlotController):
        self.algorithm_handler = algorithm_handler
        self.map_plotter = map_plotter
        self.plot_controller = plot_controller

    def _get_zorder(self, vis_element_type):
        type_zorder_map = {
            visualization_elements.CityScatter: self.config.get_config_value('map_display.scatter_zorder', int),
            visualization_elements.Line: self.config.get_config_value('map_display.line_zorder', int),
            visualization_elements.TextBoxScan: self.config.get_config_value('map_display.text_zorder', int)
        }

        return type_zorder_map[vis_element_type]

    def plot(self, vis_element: visualization_elements.VisualizationElement, display_types: list[str] = ['algorithm', 'map']):
        if 'algorithm' in display_types and self.plot_controller.should_display(
                visualization_element=vis_element,
                display_type='algorithm'):
            self.algorithm_handler.plot_element(vis_element)
        elif 'map' in display_types:
            zorder = self._get_zorder(type(vis_element))
            self.map_plotter.plot_element(vis_element, zorder=zorder)

    def get_text_box_bounds(self, visualization_element: visualization_elements.VisualizationElement):
        patch = self.map_plotter.plot_element(visualization_element, override_coord=(0, 0), zorder=1)
        bbox = patch.get_window_extent()
        x_min, y_min, x_max, y_max = bbox.x0, bbox.y0, bbox.x1, bbox.y1
        return {
            'x_min': x_min,
            'y_min': y_min,
            'x_max': x_max,
            'y_max': y_max
        }
