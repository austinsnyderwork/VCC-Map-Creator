import configparser
from shapely.geometry import Polygon

from . import algorithm_map_creator, helper_functions, poly_creation, rtree_analysis


config = configparser.ConfigParser()
config.read('config.ini')


class AlgorithmHandler:

    def __init__(self):
        self.algo_map_creator = algorithm_map_creator.AlgorithmMapCreator()
        self.rtree_analyzer = rtree_analysis.RtreeAnalyzer()

    def plot_lines(self, lines_by_origin_outpatient: dict):
        for (origin_name, outpatient_name), line_data in lines_by_origin_outpatient.items():
            poly = poly_creation.create_poly(poly_type='line', x_data=line_data['x_data'], y_data=line_data['y_data'],
                                             line_width=line_data['line_width'])
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='line poly')
            self.rtree_analyzer.add_poly(poly_class='line',
                                         poly=poly)
            self.algo_map_creator.add_poly_to_map(poly=poly)

    def plot_points(self, point_coords):
        scatter_size = float(config['dimensions']['scatter_size'])
        units_radius_per_1_scatter_size = float(config['dimensions']['units_radius_per_1_scatter_size'])
        for i, point_coord in enumerate(point_coords):
            units_radius = scatter_size * units_radius_per_1_scatter_size
            poly = poly_creation.create_poly(poly_type='scatter', center=point_coord, radius=units_radius)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='scatter poly')
            self.rtree_analyzer.add_poly(poly_class='scatter',
                                         poly=poly)
            self.algo_map_creator.add_poly_to_map(poly=poly)

    def _lookup_poly_characteristics(self, poly_type: str):
        poly_type_data = {
            'search_area': {
                'color': config['algo_display']['search_area_poly_color'],
                'transparency': config['algo_display']['search_area_poly_transparency'],
                'show_algo': config['algo_display']['show_search_area'],
                'immediately_delete': config['algo_display']['immediately_delete_search_area'],
                'should_plot': False,
                'center_view': config['algo_display']['center_view_on_search_area']
            },
            'scan': {
                'color': config['algo_display']['scan_poly_color'],
                'transparency': config['algo_display']['scan_poly_transparency'],
                'show_algo': config['algo_display']['show_can_poly'],
                'immediately_delete': config['algo_display']['immediately_delete_scan_poly'],
                'should_plot': False,
                'center_view': config['algo_display']['center_view_on_scan_poly']
            },
            'intersecting': {
                'color': config['algo_display']['intersecting_poly_color'],
                'transparency': config['algo_display']['intersecting_poly_transparency'],
                'show_algo': config['algo_display']['show_intersecting_poly'],
                'immediately_delete': config['algo_display']['immediately_delete_intersecting_poly'],
                'should_plot': False,
                'center_view': config['algo_display']['center_view_on_intersecting_poly']
            },
            'best_poly': {
                'color': config['algo_display']['best_poly_color'],
                'transparency': config['algo_display']['best_poly_transparency'],
                'show_algo': config['algo_display']['show_best_poly'],
                'immediately_delete': config['algo_display']['immediately_delete_best_poly'],
                'should_plot': True,
                'center_view': config['algo_display']['center_view_on_best_poly']
            }
        }

        return poly_type_data[poly_type]

    def plot_rectangle(self, poly: Polygon, poly_type: str, poly_class: str):
        poly_characteristics = self._lookup_poly_characteristics(poly_type=poly_type)
        if bool(poly_characteristics['should_plot']):
            self.rtree_analyzer.add_poly(poly=poly,
                                         poly_class=poly_class)

        if bool(poly_characteristics['show_algo']):
            self.algo_map_creator.add_poly_to_map(poly=poly,
                                                  center_view=bool(poly_characteristics['center_view']),
                                                  color=bool(poly_characteristics['center_view']),
                                                  transparency=float(poly_characteristics['transparency']),
                                                  immediately_remove=bool(poly_characteristics['immediately_remove']))


