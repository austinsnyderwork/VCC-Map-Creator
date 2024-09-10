import configparser
import logging
from shapely.geometry import Polygon

from . import algorithm_map_creator, helper_functions, rtree_analysis
import poly_creation

config = configparser.ConfigParser()
config.read('config.ini')


class AlgorithmHandler:

    def __init__(self):
        show_algo_display = False if config['algo_display']['show_display'] == 'False' else True
        self.algo_map_creator = algorithm_map_creator.AlgorithmMapCreator(show_display=show_algo_display)
        self.rtree_analyzer = rtree_analysis.RtreeAnalyzer()

    def plot_lines(self, lines_by_origin_outpatient: dict):
        line_color = str(config['algo_display']['line_color'])
        show_line = False if config['algo_display']['show_line'] == 'False' else True
        line_transparency = float(config['algo_display']['line_transparency'])
        immediately_remove_line = False if config['algo_display']['immediately_remove_line'] == 'False' else True
        
        for (origin_name, outpatient_name), line_data in lines_by_origin_outpatient.items():
            if origin_name == outpatient_name:
                logging.error(f"Origin and outpatient both found to be the same: {origin_name} = {outpatient_name}")
                continue
            poly = poly_creation.create_poly(poly_type='line', x_data=line_data['x_data'], y_data=line_data['y_data'],
                                             line_width=line_data['line_width'])
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='line poly')
            self.rtree_analyzer.add_poly(poly_class='line',
                                         poly=poly)
            
            self.algo_map_creator.add_poly_to_map(poly=poly,
                                                  show=show_line,
                                                  color=line_color,
                                                  transparency=line_transparency,
                                                  immediately_remove=immediately_remove_line)

    def plot_points(self, city_coords):
        scatter_size = float(config['dimensions']['scatter_size'])
        units_radius_per_1_scatter_size = float(config['dimensions']['units_radius_per_1_scatter_size'])
        
        scatter_color = config['algo_display']['scatter_color']
        show_scatter = False if config['algo_display']['show_scatter'] == 'False' else True
        scatter_transparency = float(config['algo_display']['scatter_transparency'])
        immediately_remove_scatter = False if config['algo_display']['immediately_remove_scatter'] == 'False' else True
        for i, (city_name, city_coord) in enumerate(city_coords.items()):
            units_radius = scatter_size * units_radius_per_1_scatter_size
            poly = poly_creation.create_poly(poly_type='scatter', center=city_coord, radius=units_radius)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='scatter poly')
            self.rtree_analyzer.add_poly(poly_class='scatter',
                                         poly=poly)
            self.algo_map_creator.add_poly_to_map(poly=poly,
                                                  show=show_scatter,
                                                  color=scatter_color,
                                                  transparency=scatter_transparency,
                                                  immediately_remove=immediately_remove_scatter)

    def _lookup_poly_characteristics(self, poly_type: str):
        poly_type_data = {
            'search_area': {
                'color': config['algo_display']['search_area_poly_color'],
                'transparency': config['algo_display']['search_area_poly_transparency'],
                'show_algo': config['algo_display']['show_search_area_poly'],
                'immediately_remove': config['algo_display']['immediately_remove_search_area_poly'],
                'should_plot': 'False',
                'center_view': config['algo_display']['center_view_on_search_area_poly']
            },
            'scan': {
                'color': config['algo_display']['scan_poly_color'],
                'transparency': config['algo_display']['scan_poly_transparency'],
                'show_algo': config['algo_display']['show_can_poly'],
                'immediately_remove': config['algo_display']['immediately_remove_scan_poly'],
                'should_plot': 'False',
                'center_view': config['algo_display']['center_view_on_scan_poly']
            },
            'intersecting': {
                'color': config['algo_display']['intersecting_poly_color'],
                'transparency': config['algo_display']['intersecting_poly_transparency'],
                'show_algo': config['algo_display']['show_intersecting_poly'],
                'immediately_remove': config['algo_display']['immediately_remove_intersecting_poly'],
                'should_plot': 'False',
                'center_view': config['algo_display']['center_view_on_intersecting_poly']
            },
            'best_poly': {
                'color': config['algo_display']['best_poly_color'],
                'transparency': config['algo_display']['best_poly_transparency'],
                'show_algo': config['algo_display']['show_best_poly'],
                'immediately_remove': config['algo_display']['immediately_remove_best_poly'],
                'should_plot': 'True',
                'center_view': config['algo_display']['center_view_on_best_poly']
            }
        }

        return poly_type_data[poly_type]

    def plot_rectangle(self, poly: Polygon, poly_type: str, poly_class: str):
        poly_characteristics = self._lookup_poly_characteristics(poly_type=poly_type)
        should_plot = False if poly_characteristics['should_plot'] == 'False' else True
        show_algo = False if poly_characteristics['show_algo'] == 'False' else True
        if should_plot:
            self.rtree_analyzer.add_poly(poly=poly,
                                         poly_class=poly_class)

        if show_algo:
            center_view = False if poly_characteristics['center_view'] == 'False' else True
            immediately_remove = False if poly_characteristics['immediately_remove'] == 'False' else True
            self.algo_map_creator.add_poly_to_map(poly=poly,
                                                  show=poly_characteristics['show_algo'],
                                                  center_view=center_view,
                                                  color=poly_characteristics['center_view'],
                                                  transparency=float(poly_characteristics['transparency']),
                                                  immediately_remove=immediately_remove)
            
    def find_available_poly_around_point(self, scan_poly_dimensions: dict, center_coord):
        search_height = float(config['algorithm']['search_height'])
        search_width = float(config['algorithm']['search_width'])
        search_steps = int(config['algorithm']['search_steps'])
        show_pause = float(config['algo_display']['show_pause'])

        scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                              **scan_poly_dimensions)
        search_area_poly = poly_creation.create_search_area_polygon(center_coord=center_coord,
                                                                    search_distance_height=search_height,
                                                                    search_distance_width=search_width)
        best_poly = None
        for poly, poly_type in self.rtree_analyzer.find_available_poly_around_point(scan_poly=scan_poly,
                                                                                    search_area_poly=search_area_poly,
                                                                                    search_steps=search_steps):
            poly_data = self._lookup_poly_characteristics(poly_type=poly_type)
            if poly_type == 'best_poly':
                best_poly = poly
                logging.info("Found best polygon.")
                break

            if not poly_data['show_algo']:
                continue

            self.algo_map_creator.add_poly_to_map(poly=poly,
                                                  show_pause=show_pause,
                                                  **poly_data)

        self.rtree_analyzer.add_poly(poly=best_poly,
                                     poly_class='text')
        poly_data = self._lookup_poly_characteristics(poly_type='best_poly')
        self.algo_map_creator.add_poly_to_map(poly=best_poly,
                                              **poly_data)
        display_coord = best_poly.centroid.x, best_poly.centroid.y
        return display_coord
            
        


