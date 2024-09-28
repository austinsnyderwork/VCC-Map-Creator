from typing import Union

import algorithm
import config_manager
from . import ConditionsMap, PlotController
from polygons import polygon_factory
from things.entities import entities
from things.visualization_elements import visualization_elements
from things import thing_converter
import map


class PlotManager:

    def __init__(self, config: config_manager.ConfigManager, thing_converter_: thing_converter.ThingConverter, algorithm_plotter: algorithm.AlgorithmPlotter,
                 map_plotter: map.MapPlotter):
        self.config = config
        self.thing_converter_ = thing_converter_
        self.algorithm_plotter = algorithm_plotter
        self.map_plotter = map_plotter
        self.polygon_factory_ = polygon_factory.PolygonFactory()

        self.display_plotters = {
            'algorithm': algorithm_plotter,
            'map': map_plotter
        }

    def _plot_visualization_element(self, vis_element: visualization_elements.VisualizationElement, display_type: str):
        if display_type == 'algorithm':
            self.algorithm_plotter.plot_element(vis_element)
        elif display_type == 'map':
            self.algorithm_plotter.plot_element(vis_element)

    def _get_zorder(self, vis_element_type):
        type_zorder_map = {
            visualization_elements.CityScatter: self.config.get_config_value('map_display.scatter_zorder', int),
            visualization_elements.Line: self.config.get_config_value('map_display.line_zorder', int),
            visualization_elements.TextBoxScan: self.config.get_config_value('map_display.text_zorder', int)
        }

        return type_zorder_map[vis_element_type]

    def plot(self, conditions_map: ConditionsMap, plot_controller: PlotController, entity: entities.Entity = None,
             visualization_element: visualization_elements.VisualizationElement = None):
        if entity:
        conditional_vis_element = conditions_map.get_visualization_element_for_condition(entity=entity,
                                                                                         **entity.__dict__)
        vis_element = conditional_vis_element if conditional_vis_element else self.thing_converter_.convert_thing(
            entity)
        if type(vis_element) is visualization_elements.CityScatterAndText:
            vis_element: visualization_elements.CityScatterAndText
            self.plot(conditions_map=conditions_map,
                      plot_controller=plot_controller,
                      visualization_element=vis_element.city_scatter)
            self.plot(conditions_map=conditions_map,
                      plot_controller=plot_controller,
                      visualization_element=vis_element.city_text_box)
        vis_element.poly = self.polygon_factory_.create_poly(vis_element)

        if type(vis_element) is visualization_elements.TextBoxScan:
            vis_element: visualization_elements.TextBoxScan
            text_box_bounds = self._get_text_box_bounds(visualization_element=vis_element)
            vis_element.poly = self.polygon_factory_.create_poly(vis_element=vis_element,
                                                                 **text_box_bounds)

        if plot_controller.should_display(type(vis_element), display_type='algorithm'):
            self.algorithm_plotter.plot_element(vis_element)

        if plot_controller.should_display(type(vis_element), display_type='map'):
            zorder = self._get_zorder(vis_element_type=type(vis_element))
            self.map_plotter.plot_element(vis_element, zorder)

    def _get_text_box_bounds(self, visualization_element: visualization_elements.VisualizationElement):
        patch = self.map_plotter.plot_element(visualization_element, override_coord=(0, 0), zorder=1)
        return patch
