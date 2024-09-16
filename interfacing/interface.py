import configparser
import logging
import matplotlib
from mpl_toolkits.basemap import Basemap

from .visualization_element import VisualizationElement
import algorithm
import input_output
import origin_grouping
import visualization

config = configparser.ConfigParser()
config.read('config.ini')


class Interface:

    def __init__(self):
        self.vis_map_creator = visualization.VisualizationMapCreator()

        all_colors = matplotlib.colors.CSS4_COLORS
        colors = [color for color, hex_value in all_colors.items() if visualization.is_dark_color(hex_value)]
        self.origin_groups_handler_ = origin_grouping.OriginGroupsHandler(colors=colors)

        self.algo_handler = algorithm.AlgorithmHandler()

        self.colors = []

        self.data_imported = False

    def _add_city_gpd_coord(self, row, base_map: Basemap):
        coord_dict = self.vis_map_creator.city_coords
        community = row['community']
        origin = row['point_of_origin']
        if community not in coord_dict:
            lon = row['to_lon']
            lat = row['to_lat']
            lon, lat = base_map(lon, lat)
            coord_dict[community] = {
                'latitude': lat,
                'longitude': lon
            }

        if origin not in coord_dict:
            lon = row['origin_lon']
            lat = row['origin_lat']
            lon, lat = base_map(lon, lat)
            coord_dict[origin] = {
                'latitude': lat,
                'longitude': lon
            }

    def import_data(self, vcc_file_name: str, sheet_name: str = None, variables: dict = None):
        df = input_output.get_dataframe(file_name=vcc_file_name,
                                        sheet_name=sheet_name,
                                        variables=variables)

        # Gather necessary city coordinates
        df.apply(self._add_city_gpd_coord, base_map=self.vis_map_creator.iowa_map, axis=1)
        logging.info("Added city coords.")

        df.apply(self.origin_groups_handler_.group_origins, city_coords=self.vis_map_creator.city_coords, axis=1)
        logging.info(f"Grouped origins.")

        all_colors = matplotlib.colors.CSS4_COLORS
        self.colors = [color for color, hex_value in all_colors.items() if visualization.is_dark_color(hex_value)]

        self.data_imported = True

    def create_maps(self):
        if not self.data_imported:
            raise ValueError(f"Have to import data first before calling {__name__}.")
        line_width = int(config['dimensions']['line_width'])
        line_vis_elements: list[VisualizationElement] = self.vis_map_creator.plot_lines(
            origin_groups=self.origin_groups_handler_.origin_groups,
            line_width=line_width,
            zorder=1)
        self.algo_handler.plot_lines(line_vis_elements)
        city_vis_elements = self.vis_map_creator.plot_points(origin_groups=self.origin_groups_handler_.origin_groups,
                                                             scatter_size=float(
                                                                 config['dimensions']['scatter_size']),
                                                             dual_origin_outpatient=self.origin_groups_handler_.dual_origin_outpatient,
                                                             zorder=3)
        self.algo_handler.plot_points(city_vis_elements)
        self.vis_map_creator.plot_sample_text_boxes(city_elements=city_vis_elements)
        logging.info("Finding best polygons for city vis elements.")
        self.algo_handler.find_best_polys(city_vis_elements)
        self.vis_map_creator.plot_text_boxes(city_elements=city_vis_elements, zorder=2)
        show_pause = 360
        self.vis_map_creator.show_map(show_pause=show_pause)
