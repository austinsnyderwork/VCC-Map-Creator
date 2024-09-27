
from typing import Union

import algorithm
from . import ConditionsMap, PlotController
from things.entities import entities
from things.visualization_elements import visualization_elements
from things import thing_converter
import map


class PlotManager:

    def __init__(self, thing_converter_: thing_converter.ThingConverter, algorithm_plotter: algorithm.AlgorithmPlotter,
                 map_plotter: map.MapPlotter):
        self.thing_converter = thing_converter
        self.algorithm_plotter = algorithm_plotter
        self.visualization_plotter = map_plotter

        self.display_plotters = {
            'algorithm': algorithm_plotter,
            'map': map_plotter
        }

    def _plot_visualization_element(self, vis_element: visualization_elements.VisualizationElement, display_type: str):
        if display_type == 'algorithm':
            self.algorithm_plotter.plot_element(vis_element)
        elif display_type == 'map':
            self.algorithm_plotter.plot_element(vis_element)

    def plot(self, entities_: list[entities.Entity], conditions_map: ConditionsMap, plot_controller: PlotController):
        vis_elements = []
        for entity in entities_:
            conditional_vis_element = conditions_map.get_visualization_element_for_condition(**entity.__dict__)
            if conditional_vis_element:
                vis_elements.append(conditional_vis_element)
                continue

            vis_element = self.thing_converter.convert_thing(entity)
            vis_elements.append(vis_element)

        for city in self.entities_manager.get_all_entities(entities.City):
            # !!!!Make this into a function to be reused for each entity type
            vis_element_output_algo = self._produce_visualization_element(city,
                                                                          display_type='algorithm')
            if vis_element_output_algo:
                self._plot_visualization_element(vis_element=vis_element_output_algo, display_type='algorithm')

            vis_element_output_map = self._produce_visualization_element(city,
                                                                         display_type='map')
            if vis_element_output_map:
                self._plot_visualization_element(vis_element=vis_element_output_map, display_type='map')

        for provider_assignment in self.entities_manager.get_all_entities(entities.ProviderAssignment):
            vis_element_output_algo = self._produce

        for vis_element in vis_elements:
            self._plot_visualization_element(vis_element)



