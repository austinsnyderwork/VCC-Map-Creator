import matplotlib
import pandas as pd

import entities
import environment_management


def is_dark_color(hex_color):
    # Convert hex to RGB values
    rgb = matplotlib.colors.hex2color(hex_color)
    # Calculate perceived brightness using a common formula
    brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    # A threshold to determine what counts as a "light" color
    return brightness < 0.7


class SystemInitializer:

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.environment_factory = self._create_environment_factory()

    def _create_environment_factory(self):
        cities_directory = entities.CitiesDirectory()

        all_colors = matplotlib.colors.CSS4_COLORS
        colors = [color for color, hex_value in all_colors.items() if is_dark_color(hex_value)]
        city_origin_network_handler = environment_management.CityOriginNetworkHandler(colors=colors)
        environment = environment_management.Environment(cities_directory=cities_directory,
                                                         city_origin_network_handler=city_origin_network_handler)
        environment_factory = environment_management.EnvironmentFactory(environment=environment,
                                                                        df=df)
        return environment_factory
