import pandas as pd

from . import data_functions, helper_functions
import algorithm
import visualization_elements
import entities
import environment_management
from environment_management import VisualizationElementPlotController, plot_configurations
import startup_factory
import visualization


class ApplicationManager:

    def __init__(self, df: pd.DataFrame,
                 startup_factory_: startup_factory.StartupFactory = None,
                 visualization_plotter: visualization.VisualizationPlotter = None,
                 algorithm_handler: algorithm.AlgorithmHandler = None):
        self.df = df
        startup_factory_ = startup_factory_ or startup_factory.StartupFactory(df=self.df)
        self.visualization_plotter = visualization_plotter or visualization.VisualizationPlotter()
        self.environment = startup_factory_.create_filled_environment(
            coord_converter_func=self.visualization_plotter.convert_coord_to_display)
        self.entities_manager = visualization_elements.VisualizationElementsManager()

        self.algorithm_handler = algorithm_handler or algorithm.AlgorithmHandler()

    def create_line_map(self):
        entity_plot_controller = environment_management.VisualizationElementPlotController()
        for entity in self.environment.entities.values():
            if entity_plot_controller.should_display(type(entity))
        for polygon in self.polygons.values():
            if entity_plot_controller.should_display(type(polygon), )
        self.visualization_plotter.plot_line()

    def create_highest_volume_line_map(self, number_of_results: int):
        highest_volume_cities = data_functions.get_top_volume_incoming_cities(df=self.df,
                                                                              num_results=number_of_results)


    def create_number_of_visiting_providers_map(self):
        conditions_map = plot_configurations.NumberOfVisitingProvidersConditions()
        vis_element_plot_controller = plot_configurations.VisualizationElementPlotController(
            entity_conditions_map=conditions_map,
            should_plot_origin_lines=False,
            should_plot_outpatient_lines=False,
            should_plot_origin_text_box=False
        )
        city_objs = list(self.environment.cities_directory.values())
        for iteration, city_obj in enumerate(city_objs):
            conditions_map.get_visualization_element_for_condition(num_visiting_providers=len(city_obj.visiting_providers))
            if vis_element_plot_controller.should_display(entity_type=entities.City,
                                                          iterations=iteration,
                                                          display_type='algorithm'):
                self.algorithm_handler.plot_point()
        """
        For every city in environment entities, plot that city scatter if it is one of the highest volume cities.
        Then, plot a text box for every city."""


