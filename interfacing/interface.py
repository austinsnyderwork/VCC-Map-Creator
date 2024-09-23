import configparser
import copy
import heapq
import logging
import matplotlib
from mpl_toolkits.basemap import Basemap

from .visualization_element import VisualizationElement
import algorithm
import entities
import environment_management
import input_output
from utils.helper_functions import get_config_value
import visualization

config = configparser.ConfigParser()
config.read('config.ini')


class Interface:

    def __init__(self):
        all_colors = matplotlib.colors.CSS4_COLORS
        colors = [color for color, hex_value in all_colors.items() if visualization.is_dark_color(hex_value)]

        self.environment_factory = environment_management.EnvironmentFactory()
        self.vis_map_creator = visualization.VisualizationMapCreator()
        self.algo_handler = algorithm.AlgorithmHandler()

        self.data_imported = False
        self.df = None

    """
    Just for testing, really
    def _load_city_text_boxes(self, city_vis_elements, use_pickle: False):
        city_vis_elements_file_path = 'vcc_maps/city_vis_elements.pkl'
        if use_pickle and os.path.exists(city_vis_elements_file_path):
            with open(city_vis_elements_file_path, 'rb') as file:
                city_vis_elements = pickle.load(file)
        else:
            self.vis_map_creator.plot_sample_text_boxes(city_elements=city_vis_elements)
            with open(city_vis_elements_file_path, 'wb') as file:
                pickle.dump(city_vis_elements, file)
        return city_vis_elements"""

    def _convert_to_display_coordinates(self, coord: tuple):
        lon, lat = self.vis_map_creator.iowa_map(coord)
        return lon, lat

    def import_data(self, vcc_file_name: str, sheet_name: str = None, origins_to_group_together: dict = None):
        self.df = input_output.get_dataframe(file_name=vcc_file_name,
                                             sheet_name=sheet_name)
        cities_directory =
        environment = environment_management.Environment()
        self.environment_factory = environment_management.EnvironmentFactory(environment=environment,
                                                                             df=self.df)

    def _should_plot_text(self, city_scatter: entities.CityScatter, plot_origins: bool, plot_outpatients: bool):
        if city_scatter.site_type == 'origin' and not plot_origins:
            return False
        elif city_scatter.site_type == 'outpatient' and not plot_outpatients:
            return False
        elif city_scatter.site_type == 'both' and not plot_origins and not plot_outpatients:
            return False
        return True

    def _plot_text_boxes(self, city_scatters: list[entities.CityScatter], plot_origins: bool, plot_outpatients: bool):
        valid_city_scatters = []
        for city_scatter in city_scatters:
            if not self._should_plot_text(city_scatter=city_scatter,
                                          plot_origins=plot_origins,
                                          plot_outpatients=plot_outpatients):
                continue

            valid_city_scatters.append(city_scatter)
        self.vis_map_creator.plot_sample_text_boxes(valid_city_scatters=valid_city_scatters)
        logging.info("Finding best polygons for city vis elements.")
        self.algo_handler.find_best_polys(valid_city_scatters)
        self.vis_map_creator.plot_text_boxes(city_scatters=valid_city_scatters, zorder=2)

    def create_line_map(self, origin_groups_handler_: origin_grouping.OriginGroupsHandler, variables: dict = None,
                        plot_origins_text: bool = True, plot_outpatients_text: bool = True):
        if not self.data_imported:
            raise ValueError(f"Have to import data first before calling {__name__}.")

        line_width = get_config_value(config, 'dimensions.line_width', int)
        lines = self.vis_map_creator.plot_lines(
            origin_groups=origin_groups_handler_.origin_groups,
            line_width=line_width,
            zorder=1)
        self.algo_handler.plot_lines(lines)
        city_vis_elements = self.vis_map_creator.plot_points(origin_groups=origin_groups_handler_.origin_groups,
                                                             scatter_size=float(config['dimensions']['scatter_size']),
                                                             dual_origin_outpatients=origin_groups_handler_.dual_origin_outpatient,
                                                             zorder=3)
        self.algo_handler.plot_points(city_vis_elements)
        self._plot_text_boxes(city_vis_elements, plot_origins=plot_origins_text, plot_outpatients=plot_outpatients_text)
        show_pause = 360
        self.vis_map_creator.show_map(show_pause=show_pause)

    def _get_top_outreach_volume_cities(self, num_results: int):
        origin_counts = self.df['point_of_origin'].value_counts()
        origin_counts = origin_counts.to_dict()

        counts_dict = {}
        for key, value in origin_counts.items():
            if value not in counts_dict:
                counts_dict[value] = []
            counts_dict[value].append(key)

        top_counts = heapq.nlargest(num_results, list(counts_dict.keys()))
        top_dict = {count: cities for count, cities in counts_dict.items() if count in top_counts}
        top_cities = []
        for count, cities in top_dict.items():
            top_cities.extend(cities)
        return top_cities

    def create_highest_volume_line_map(self, num_results: int):
        top_origins = self._get_top_outreach_volume_cities(num_results=num_results)
        origin_groups_handler_ = copy.deepcopy(self.origin_groups_handler_)
        origin_groups_handler_.filter_origin_groups(filter_origins=top_origins)
        origin_groups_handler_.dual_origin_outpatient = []
        self.create_line_map(origin_groups_handler_=origin_groups_handler_,
                             plot_origins_text=True,
                             plot_outpatients_text=False)

    @staticmethod
    def _count_outpatient_visiting_clinics(row, num_visiting_clinics: dict):
        origin = row['point_of_origin']
        outpatient = row['community']

        if outpatient not in num_visiting_clinics:
            num_visiting_clinics[outpatient] = {
                'count': 0,
                'visiting_clinics': set()
            }

        if origin not in num_visiting_clinics[outpatient]['visiting_clinics']:
            num_visiting_clinics[outpatient]['count'] += 1
            num_visiting_clinics[outpatient]['visiting_clinics'].add(origin)

    def create_outpatient_num_visiting_clinics_map(self):
        if not self.data_imported:
            raise ValueError(f"Have to import data first before calling {__name__}.")

        num_visiting_clinics = {}
        self.df.apply(self._count_outpatient_visiting_clinics, axis=1, num_visiting_clinics=num_visiting_clinics)

        visiting_list = []
        for outpatient, data in num_visiting_clinics.items():
            visiting_list.append({
                'name': outpatient,
                'num_visiting_clinics': data['count']
            })

        city_elements = self.vis_map_creator.plot_num_visiting_clinics_map(visiting_list)

        show_pause = 360
        self.vis_map_creator.show_map(show_pause=show_pause)

