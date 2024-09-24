import pandas as pd

from . import data_preparer, helper_functions
import algorithm
import entities
import environment_management
from environment_management import plot_configurations
import visualization


class ApplicationManager:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.environment_factory = self._create_environment_factory()
        self.visualization_map_creator = visualization.VisualizationMapCreator()
        self.algorithm_handler = algorithm.AlgorithmHandler()

    def _create_environment_factory(self):
        cities_directory = entities.CitiesDirectory()

        colors = helper_functions.get_colors()
        city_origin_network_handler = environment_management.CityOriginNetworkHandler(colors=colors)
        environment = environment_management.Environment(cities_directory=cities_directory,
                                                         city_origin_network_handler=city_origin_network_handler)
        environment_factory = environment_management.EnvironmentFactory(environment=environment,
                                                                        df=self.df)
        return environment_factory

    def initialize_applications(self, city_name_changes: dict):
        self.environment_factory.fill_environment(coord_converter=self.visualization_map_creator.convert_coord_to_display,
                                                  city_name_changes=city_name_changes)

    def create_line_map(self):
        entity_plot_controller = plot_configurations.EntityPlotController()

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


