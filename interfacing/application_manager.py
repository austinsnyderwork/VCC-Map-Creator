import matplotlib
from mpl_toolkits.basemap import Basemap
import pandas as pd

import algorithm
import entities
import environment_management
import visualization


def is_dark_color(hex_color):
    # Convert hex to RGB values
    rgb = matplotlib.colors.hex2color(hex_color)
    # Calculate perceived brightness using a common formula
    brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    # A threshold to determine what counts as a "light" color
    return brightness < 0.7


class ApplicationManager:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.environment_factory = self._create_environment_factory()
        self.visualization_map_creator = visualization.VisualizationMapCreator()
        self.algorithm_handler = algorithm.AlgorithmHandler()

    def _create_environment_factory(self):
        cities_directory = entities.CitiesDirectory()

        all_colors = matplotlib.colors.CSS4_COLORS
        colors = [color for color, hex_value in all_colors.items() if is_dark_color(hex_value)]
        city_origin_network_handler = environment_management.CityOriginNetworkHandler(colors=colors)
        environment = environment_management.Environment(cities_directory=cities_directory,
                                                         city_origin_network_handler=city_origin_network_handler)
        environment_factory = environment_management.EnvironmentFactory(environment=environment,
                                                                        df=self.df)
        return environment_factory

    def _convert_coord_to_display(self, coord: tuple):
        convert_lon, convert_lat = self.visualization_map_creator.iowa_map(coord)
        return convert_lon, convert_lat

    def initialize_applications(self, city_name_changes: dict, ):
        self.environment_factory.fill_environment(coord_converter=self._convert_coord_to_display,
                                                  city_name_changes=city_name_changes)
