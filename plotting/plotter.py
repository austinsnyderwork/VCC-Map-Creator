
import environment_management
from environment_management import plot_configurations, VisualizationElementPlotController
from things.entities import entities


class Plotter:

    def __init__(self, entities: list[entities.Entity], entity_converter: environment_management.EntityToVisualizationElementConverter,
                 conditions_map: plot_configurations.ConditionsMap, plot_controller: VisualizationElementPlotController):
        self.entities = entities
        self.entity_converter = entity_converter
        self.conditions_map = conditions_map
        self.plot_controller = plot_controller

    def _get_visualization_elements(self):
        vis_elements = []
        for entity in self.entities:
            vis_element = self.conditions_map.get_visualization_element_for_condition(entity=entity)
            if vis_element:
                vis_elements.append(vis_element)
                continue

            for vis_element in self.entity_converter.convert_entity(entity):
                vis_elements.append(vis_element)

    def plot(self):
        vis_elements = []
        for entity in self.entities:
            vis_element = self.conditions_map.get_visualization_element_for_condition(entity=entity)
            if vis_element:
                vis_elements.append(vis_element)
                continue


