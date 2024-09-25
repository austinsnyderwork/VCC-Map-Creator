import entities
from environment_management import VisualizationElementPlotController
from environment_management import plot_configurations


class Plotter:

    def __init__(self, entities: list[entities.Entity], conditions_map: plot_configurations.ConditionsMap, plot_controller: VisualizationElementPlotController):
        self.entities = entities
        self.conditions_map = conditions_map
        self.plot_controller = plot_controller

    def plot(self):
        for entity in self.entities:
            if type(entity)