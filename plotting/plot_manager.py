from typing import Union

import algorithm
import config_manager
from . import PlotController
from things.visualization_elements import visualization_elements
import map


class PlotManager:

    def __init__(self, algorithm_handler: algorithm.AlgorithmHandler,
                 map_plotter: map.MapPlotter):
        self.algorithm_handler = algorithm_handler
        self.map_plotter = map_plotter

    def _get_zorder(self, vis_element_type):
        type_zorder_map = {
            visualization_elements.CityScatter: self.config.get_config_value('map_display.scatter_zorder', int),
            visualization_elements.Line: self.config.get_config_value('map_display.line_zorder', int),
            visualization_elements.TextBoxScan: self.config.get_config_value('map_display.text_zorder', int)
        }

        return type_zorder_map[vis_element_type]

    def plot(self, vis_element: visualization_elements.VisualizationElement, display_types: list[str] = ['algorithm', 'map']):
        if 'algorithm' in display_types:
            self.algorithm_handler.plot_element(vis_element)
        elif 'map' in display_types:
            zorder = self._get_zorder(type(vis_element))
            self.map_plotter.plot_element(vis_element, zorder=zorder)

    def get_text_box_bounds(self, visualization_element: visualization_elements.VisualizationElement):
        patch = self.map_plotter.plot_element(visualization_element, override_coord=(0, 0), zorder=1)
        return patch.bounds
