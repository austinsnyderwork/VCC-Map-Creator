import configparser
import logging
import matplotlib
from mpl_toolkits.basemap import Basemap

from algorithm import rtree_analysis
import algorithm
import input_output
import origin_grouping
import poly_creation
import visualization

config = configparser.ConfigParser()
config.read('config.ini')


class Interface:

    def __init__(self):
        self.vis_map_creator = visualization.VisualizationMapCreator()
        self.origin_groups_handler_ = origin_grouping.OriginGroupsHandler()

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
        df.apply(self._add_city_gpd_coord, axis=1)
        logging.info("Added city coords.")

        df.apply(self.origin_groups_handler_.group_origins, axis=1)
        logging.info(f"Grouped origins.")

        all_colors = matplotlib.colors.CSS4_COLORS
        self.colors = [color for color, hex_value in all_colors.items() if visualization.is_dark_color(hex_value)]

        self.data_imported = True

    @staticmethod
    def _determine_search_area_bounds(city_lon, city_lat):
        search_area_bounds = {
            'min_x': city_lon - float(config['algorithm']['search_width']),
            'min_y': city_lat - float(config['algorithm']['search_height']),
            'max_x': city_lon + float(config['algorithm']['search_width']),
            'max_y': city_lat + float(config['algorithm']['search_height'])
        }
        return search_area_bounds

    def _handle_text_boxes(self, points_by_city: dict):
        text_box_display_coords = {}
        for city_name, point in points_by_city.items():
            # Have to input the text into the map to see its dimensions on our view
            text_box, text_box_dimensions = self.vis_map_creator.get_text_box_dimensions(city_name=city_name,
                                                                                         font=config['viz_display'][
                                                                                             'font'],
                                                                                         font_size=int(
                                                                                             config['viz_display'][
                                                                                                 'font_size']),
                                                                                         font_weight=
                                                                                         config['viz_display'][
                                                                                             'font_weight'])
            self.algo_handler.find_available_poly_around_point(scan_poly_dimensions=text_box_dimensions,
                                                               center_coord=point)

    def create_maps(self):
        if not self.data_imported:
            raise ValueError(f"Have to import data first before calling {__name__}.")
        line_width = float(config['dimensions']['line_width'])
        lines_by_origin_outpatient = self.vis_map_creator.plot_lines(
            origin_groups=self.origin_groups_handler_.origin_groups,
            line_width=line_width)
        lines_data_dict = {}
        for (origin_name, outpatient_name), line in lines_by_origin_outpatient.items():
            lines_data_dict[(origin_name, outpatient_name)] = {
                'x_data': line.get_xdata(),
                'y_data': line.get_ydata(),
                'line_width': line_width
            }
        self.algo_handler.plot_lines(lines_data_dict)
        points_by_city = self.vis_map_creator.plot_points(origin_groups=self.origin_groups_handler_.origin_groups,
                                                          scatter_size=float(config['dimensions']['scatter_size']),
                                                          dual_origin_outpatient=self.origin_groups_handler_.dual_origin_outpatient)
        self.algo_handler.plot_points(points_by_city)
        city_display_coords = self._handle_text_boxes(points_by_city)
        self.vis_map_creator.plot_text_boxes(origin_groups=self.origin_groups_handler_.origin_groups,
                                             city_display_coords=city_display_coords)
