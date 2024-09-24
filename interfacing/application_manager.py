import matplotlib
import pandas as pd

import algorithm
import configparser
import entities
import environment_management
from utils.helper_functions import get_config_value
import visualization


config = configparser.ConfigParser()
config.read('config.ini')


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

    def initialize_applications(self, city_name_changes: dict):
        self.environment_factory.fill_environment(coord_converter=self._convert_coord_to_display,
                                                  city_name_changes=city_name_changes)

    def create_line_map(self, city_origin_network_handler: environment_management.CityOriginNetworkHandler,
                        variables: dict = None):
        lines = self.visualization_map_creator.plot_lines(
            origin_groups=origin_groups_handler_.origin_groups,
            line_width=get_config_value(config, 'dimensions.line_width', int),
            zorder=1)
        self.algorithm_handler.plot_lines(lines)
        city_vis_elements = self.visualization_map_creator.plot_points(
            origin_groups=origin_groups_handler_.origin_groups,
            scatter_size=float(config['dimensions']['scatter_size']),
            dual_origin_outpatients=origin_groups_handler_.dual_origin_outpatient,
            zorder=3)
        self.algorithm_handler.plot_points(city_vis_elements)
        self._plot_text_boxes(city_vis_elements)
        show_pause = 360
        self.visualization_map_creator.show_map(show_pause=show_pause)

    def create_number_of_visiting_providers_map(self):
        x=0

    def _plot_text_boxes(self, city_scatters: list[entities.CityScatter]):
        valid_city_scatters = []
        for city_scatter in city_scatters:
            if not self.plot_controller.should_plot(city_scatter=city_scatter):
                continue

            valid_city_scatters.append(city_scatter)
        self.vis_map_creator.plot_sample_text_boxes(valid_city_scatters=valid_city_scatters)
        logging.info("Finding best polygons for city vis elements.")
        self.algo_handler.find_best_polys(valid_city_scatters)
        self.vis_map_creator.plot_text_boxes(city_scatters=valid_city_scatters, zorder=2)



