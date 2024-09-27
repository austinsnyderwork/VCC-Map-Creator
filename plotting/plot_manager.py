
from typing import Union

import algorithm
from . import ConditionsMap, PlotController
from polygons import polygon_factory
from things.entities import entities
from things.visualization_elements import visualization_elements
from things import thing_converter
import map


class PlotManager:

    def __init__(self, thing_converter_: thing_converter.ThingConverter, algorithm_plotter: algorithm.AlgorithmPlotter,
                 map_plotter: map.MapPlotter):
        self.thing_converter_ = thing_converter_
        self.algorithm_plotter = algorithm_plotter
        self.map_plotter = map_plotter

        self.display_plotters = {
            'algorithm': algorithm_plotter,
            'map': map_plotter
        }

    def _plot_visualization_element(self, vis_element: visualization_elements.VisualizationElement, display_type: str):
        if display_type == 'algorithm':
            self.algorithm_plotter.plot_element(vis_element)
        elif display_type == 'map':
            self.algorithm_plotter.plot_element(vis_element)

    def plot(self, entity: entities.Entity, conditions_map: ConditionsMap, plot_controller: PlotController, zorder: int):
        conditional_vis_element = conditions_map.get_visualization_element_for_condition(**entity.__dict__)
        vis_element = conditional_vis_element if conditional_vis_element else self.thing_converter_.convert_thing(entity)
        if type(vis_element) is visualization_elements.TextBoxScan:
            vis_element: visualization_elements.TextBoxScan
            text_box_bounds = self._get_text_box_bounds(visualization_element=vis_element)
            vis_element.poly = polygon_factory.create_poly(poly_type='rectangle',
                                                           **text_box_bounds)

        if plot_controller.should_display(type(vis_element), display_type='algorithm'):
            self.algorithm_plotter.plot_element(vis_element)

        if plot_controller.should_display(type(vis_element), display_type='map'):
            self.map_plotter.plot_element(vis_element, zorder)

    def _get_text_box_bounds(self, visualization_element: visualization_elements.VisualizationElement):
        patch = self.map_plotter.plot_element(visualization_element, override_coord=(0, 0), zorder=1)
        return patch



