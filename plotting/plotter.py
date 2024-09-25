
from typing import Union

import environment_management
from environment_management import plot_configurations, VisualizationElementPlotController
from things.entities import entities
from things.visualization_elements import visualization_elements


class Plotter:

    def __init__(self, entities_: list[entities.Entity], entity_converter: environment_management.EntityToVisualizationElementConverter,
                 conditions_map: plot_configurations.ConditionsMap, plot_controller: VisualizationElementPlotController):
        self.entities_ = entities_
        self.entity_converter = entity_converter
        self.conditions_map = conditions_map
        self.plot_controller = plot_controller

    def _get_visualization_element(self, entity: entities.Entity, iterations: int, display_type: str) -> Union[list, None]:
        if not self.plot_controller.should_display(entity, iterations=iterations, display_type=display_type):
            return None

        # Function returns None if there's no corresponding condition for this entity type
        vis_element = self.conditions_map.get_visualization_element_for_condition(entity=entity)
        if vis_element:
            return vis_element

        return self.entity_converter.convert_entity(entity)

    def _plot_visualization_element(self, vis_element: visualization_elements.VisualizationElement):


    def plot(self):
        vis_elements = {
            'algorithm': [],
            'map': []
        }
        for entity in self.entities_:
            vis_element_output_algo = self._get_visualization_element(entity)
            for vis_ele in vis_element_output:
                vis_elements.append(vis_ele)

        for vis_element in vis_elements:
            self._plot_visualization_element(vis_element)



