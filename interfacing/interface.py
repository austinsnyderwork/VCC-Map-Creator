import configparser
import logging
from algorithm import rtree_analysis

import algorithm
import input_output
import visualization


config = configparser.ConfigParser()
config.read('config.ini')


class Interface:

    def __init__(self):
        self.vis_map_creator = visualization.VisualizationMapCreator()
        self.algo_handler = algorithm.AlgorithmHandler()

        self.city_coords = {}

    def _add_city_gpd_coord(self, row):
        community = row['community']
        origin = row['point_of_origin']
        if community not in self.city_coords:
            self.city_coords[community] = {
                'latitude': row['to_lat'],
                'longitude': row['to_lon']
            }

        if origin not in self.city_coords:
            self.city_coords[origin] = {
                'latitude': row['origin_lat'],
                'longitude': row['origin_lon']
            }

    def import_data(self, vcc_file_name: str, sheet_name:str = None, variables: dict = None):
        df = input_output.get_dataframe(file_name=vcc_file_name,
                                        sheet_name=sheet_name,
                                        variables=variables)

        # Gather necessary city coordinates
        df.apply(self._add_city_gpd_coord, axis=1)
        logging.info("Added city coords.")

    def create_maps(self):
        lines = self.vis_map_creator.plot_lines(line_width=float(config['dimensions']['line_width']),
                                                city_coords=self.city_coords)
        self.algo_handler.plot_lines()
        points = self.vis_map_creator.plot_points(scatter_size=float(config['dimensions']['scatter_size']),
                                                  city_coords=self.city_coords)
        for city_name, point in points:
            city_coord = self.city_coords[city_name]
            search_area_bounds = {
                'min_x': city_coord[0] - config['algorithm']['search_width'],
                'min_y': city_coord[1] - config['algorithm']['search_height'],
                'max_x': city_coord[0] + config['algorithm']['search_width'],
                'max_y': city_coord[1] + config['algorithm']['search_height']
            }
            text_box, text_box_dimensions = self.vis_map_creator.get_text_box_dimensions(city_name=city_name,
                                                                                         font=config['viz_display']['font'],
                                                                                         font_size=int(
                                                                                           config['viz_display']['font_size']),
                                                                                         font_weight=config['viz_display'][
                                                                                           'font_weight'])
            text_width = text_box_dimensions['max_x'] - text_box_dimensions['min_x']
            text_height = text_box_dimensions['max_y'] - text_box_dimensions['min_y']
            poly_type_data = {
                'search_area': {
                    'color': config['algo_display']['search_area_poly_color'],
                    'transparency': config['algo_display']['search_area_poly_transparency']
                },
                'scan': {
                    'color': config['algo_display']['scan_poly_color'],
                    'transparency': config['algo_display']['scan_poly_transparency']
                }
            }
            for poly, poly_type in self.rtree_analyzer.find_available_poly_around_point(search_area_bounds=search_area_bounds,
                                                                                        city_coord=city_coord,
                                                                                        text_width=text_width,
                                                                                        text_height=text_height):
                poly_data = poly_type_data[poly_type]
                self.algo

            visualization.move_text_box(text_box=text_box,
                                        lon=poly.centroid.x,
                                        lat=poly.centroid.y)
        self.algorithm_handler.
