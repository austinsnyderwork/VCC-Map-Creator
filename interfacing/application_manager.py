import pandas as pd

from . import data_functions, helper_functions
import algorithm
import config_manager
import environment_management
from environment_management import VisualizationElementPlotController, plot_configurations
import plotting
import startup_factory
import things
from things import visualization_elements
from things import entities
import visualization


class ApplicationManager:

    def __init__(self, df: pd.DataFrame,
                 startup_factory_: startup_factory.StartupFactory = None,
                 visualization_plotter: visualization.VisualizationPlotter = None,
                 algorithm_handler: algorithm.AlgorithmHandler = None):
        self.df = df
        self.config = config_manager.ConfigManager()
        self.entities_manager = entities.EntitiesManager()
        startup_factory_ = startup_factory_ or startup_factory.StartupFactory(df=self.df,
                                                                              entities_manager=self.entities_manager)
        self.visualization_plotter = visualization_plotter or visualization.VisualizationPlotter(config=self.config)
        startup_factory_.fill_entities_manager(coord_converter_func=self.visualization_plotter.convert_coord_to_display)
        self.vis_elements_manager = visualization_elements.VisualizationElementsManager()

        self.algorithm_handler = algorithm_handler or algorithm.AlgorithmHandler()

    def create_line_map(self):
        entity_plot_controller = environment_management.VisualizationElementPlotController()
        for entity in self.environment.things.values():
            if entity_plot_controller.should_display(type(entity))
        for polygon in self.polygons.values():
            if entity_plot_controller.should_display(type(polygon), )
        self.visualization_plotter.plot_line()

    def create_highest_volume_line_map(self, number_of_results: int):
        highest_volume_cities = data_functions.get_top_volume_incoming_cities(df=self.df,
                                                                              num_results=number_of_results)
        vis_element_plot_controller = plot_configurations.VisualizationElementPlotController(
            config=self.config,
            show_visiting_text_boxes=False
        )
        conditions_map = plot_configurations.HighestCityVisitingVolumeConditions(highest_volume_cities=highest_volume_cities)
        plot = plotting.Plotter(entities_manager_=self.entities_manager,
                                plot_controller=vis_element_plot_controller,
                                conditions_map=conditions_map,
                                entity_converter=things.thing_converter.convert_thing)
        plot.plot()

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


