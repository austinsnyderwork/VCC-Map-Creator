import pandas as pd

from . import data_functions, helper_functions
import algorithm
import entities
import environment_management
from environment_management import city_origin_network_handler, plot_configurations
import startup_factory
import visualization


class ApplicationManager:

    def __init__(self, df: pd.DataFrame,
                 startup_factory_: startup_factory.StartupFactory = None,
                 visualization_plotter: visualization.VisualizationPlotter = None,
                 algorithm_handler: algorithm.AlgorithmHandler = None):
        self.df = df
        startup_factory_ = startup_factory_ or startup_factory.StartupFactory(df=self.df)
        self.environment = startup_factory_.create_filled_environment()
        self.visualization_plotter = visualization_plotter or visualization.VisualizationPlotter()
        self.algorithm_handler = algorithm_handler or algorithm.AlgorithmHandler()

    def create_line_map(self):
        entity_plot_controller = plot_configurations.EntityPlotController()
        self.visualization_plotter.plot_line()

    def create_number_of_visiting_providers_map(self, number_of_results: int):
        highest_volume_cities = data_preparer.get_top_volume_incoming_cities(df=self.df,
                                                                             num_results=number_of_results)
        conditions_map = plot_configurations.NumberOfVisitingProvidersConditions(highest_volume_cities=highest_volume_cities)
        entity_plot_controller = plot_configurations.EntityPlotController(
            entity_conditions_map=conditions_map,
            should_plot_origin_lines=False,
            should_plot_outpatient_lines=False,
            should_plot_origin_text_box=False
        )


