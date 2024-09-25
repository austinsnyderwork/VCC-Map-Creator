
import environment_management
from environment_management import entities, plot_configurations, VisualizationElementPlotController


class Plotter:

    def __init__(self, entities: list[entities.Entity], conditions_map: plot_configurations.ConditionsMap,
                 plot_controller: VisualizationElementPlotController):
        self.entities = entities
        self.conditions_map = conditions_map
        self.plot_controller = plot_controller

    def _get_visualization_elmements(self):
        vis_elements = []
        for entity in self.entities:
            vis_element = self.conditions_map.get_visualization_element_for_condition(entity=entity)
            if vis_element:
                vis_elements.append(vis_element)
                continue

            vis_element = create_default_visualization_element(entity)

    def plot(self):
        for entity in self.entities:
            vis_element = self.conditions_map.get_visualization_element_for_condition(entity=entity)
            if vis_element:

