import configparser
import logging
from shapely.geometry import Polygon

from utils.helper_functions import get_config_value
from . import algorithm_map_creator, helper_functions, rtree_analysis
import poly_creation
from .poly_management import PolyGroup, TypedPolygon, PolyGroupManager
import visualization

config = configparser.ConfigParser()
config.read('config.ini')


class AlgorithmHandler:

    def __init__(self):
        show_algo_display = False if config['algo_display']['show_display'] == 'False' else True
        self.algo_map_creator = algorithm_map_creator.AlgorithmMapCreator(show_display=show_algo_display)
        self.rtree_analyzer = rtree_analysis.RtreeAnalyzer()

    def plot_lines(self, line_eles: list[visualization.VisualizationElement]):
        line_color = str(config['algo_display']['line_color'])
        show_line = False if config['algo_display']['show_line'] == 'False' else True
        line_transparency = float(config['algo_display']['line_transparency'])
        immediately_remove_line = False if config['algo_display']['immediately_remove_line'] == 'False' else True

        t_polys = []
        for line_ele in line_eles:
            poly = poly_creation.create_poly(poly_type='line', x_data=line_ele.x_data, y_data=line_ele.y_data,
                                             line_width=line_ele.line_width)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='line poly')
            t_poly = TypedPolygon(poly=poly,
                                  poly_type='line')
            t_polys.append(t_poly)
            self.rtree_analyzer.add_poly(poly_class='line',
                                         t_poly=t_poly)
            self.algo_map_creator.add_poly_to_map(poly=poly,
                                                  show_algo=show_line,
                                                  color=line_color,
                                                  transparency=line_transparency,
                                                  immediately_remove=immediately_remove_line)
        return t_polys


    def plot_points(self, scatter_eles: list[visualization.VisualizationElement]):
        scatter_size = float(config['dimensions']['scatter_size'])
        units_radius_per_1_scatter_size = float(config['dimensions']['units_radius_per_1_scatter_size'])

        scatter_color = config['algo_display']['scatter_color']
        show_scatter = False if config['algo_display']['show_scatter'] == 'False' else True
        scatter_transparency = float(config['algo_display']['scatter_transparency'])
        immediately_remove_scatter = False if config['algo_display']['immediately_remove_scatter'] == 'False' else True
        t_polys = []
        for scatter_ele in scatter_eles:
            units_radius = scatter_size * units_radius_per_1_scatter_size
            poly = poly_creation.create_poly(poly_type='scatter', center=scatter_ele.coord, radius=units_radius)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='scatter poly')
            t_poly = TypedPolygon(poly=poly,
                                  poly_type='scatter')
            t_polys.append(t_poly)
            self.rtree_analyzer.add_poly(poly_class='scatter',
                                         t_poly=t_poly)
            self.algo_map_creator.add_poly_to_map(poly=t_poly,
                                                  show_algo=show_scatter,
                                                  color=scatter_color,
                                                  transparency=scatter_transparency,
                                                  immediately_remove=immediately_remove_scatter)
        return t_polys

    def _reduce_poly_width(self, poly: Polygon, width_adjustment: float):
        x_min, y_min, x_max, y_max = poly.bounds
        poly_width = x_max - x_min
        width_adjust_percent = width_adjustment / 100.0
        width_change = poly_width * width_adjust_percent
        x_min = x_min + (width_change / 2)
        x_max = x_max - (width_change / 2)
        poly = poly_creation.create_poly(poly_type='rectangle',
                                         x_min=x_min,
                                         y_min=y_min,
                                         x_max=x_max,
                                         y_max=y_max)
        return poly

    def _lookup_poly_characteristics(self, poly_type: str):
        poly_type_data = {
            'search_area': {
                'color': config['algo_display']['search_area_poly_color'],
                'transparency': float(config['algo_display']['search_area_poly_transparency']),
                'show_algo': False if config['algo_display']['show_search_area_poly'] == 'False' else True,
                'immediately_remove': False if config['algo_display'][
                                                   'immediately_remove_search_area_poly'] == 'False' else True,
                'should_plot': False,
                'center_view': False if config['algo_display']['center_view_on_search_area_poly'] == 'False' else True
            },
            'scan_poly': {
                'color': config['algo_display']['scan_poly_color'],
                'transparency': float(config['algo_display']['scan_poly_transparency']),
                'show_algo': False if config['algo_display']['show_scan_poly'] == 'False' else True,
                'immediately_remove': False if config['algo_display'][
                                                   'immediately_remove_scan_poly'] == 'False' else True,
                'should_plot': False,
                'center_view': False if config['algo_display']['center_view_on_scan_poly'] == 'False' else True
            },
            'intersecting': {
                'color': config['algo_display']['intersecting_poly_color'],
                'transparency': float(config['algo_display']['intersecting_poly_transparency']),
                'show_algo': False if config['algo_display']['show_intersecting_poly'] == 'False' else True,
                'immediately_remove': False if config['algo_display'][
                                                   'immediately_remove_intersecting_poly'] == 'False' else True,
                'should_plot': False,
                'center_view': False if config['algo_display']['center_view_on_intersecting_poly'] == 'False' else True
            },
            'best_poly': {
                'color': config['algo_display']['best_poly_color'],
                'transparency': float(config['algo_display']['best_poly_transparency']),
                'show_algo': False if config['algo_display']['show_best_poly'] == 'False' else True,
                'immediately_remove': False if config['algo_display'][
                                                   'immediately_remove_best_poly'] == 'False' else True,
                'should_plot': False,
                'center_view': False if config['algo_display']['center_view_on_best_poly'] == 'False' else True
            },
            'poly_finalist': {
                'color': config['algo_display']['poly_finalist_color'],
                'transparency': float(config['algo_display']['poly_finalist_transparency']),
                'show_algo': False if config['algo_display']['show_poly_finalist'] == 'False' else True,
                'immediately_remove': False if config['algo_display'][
                                                   'immediately_remove_poly_finalist'] == 'False' else True,
                'should_plot': False,
                'center_view': False if config['algo_display']['center_view_on_poly_finalist'] == 'False' else True
            }
        }
        return poly_type_data[poly_type]

    def _scan_poly_outside_of_search_area(self, scan_poly, search_area_poly):
        extruding_scan_poly = scan_poly.difference(search_area_poly)

        return not extruding_scan_poly.is_empty

    def _create_scan_poly(self, scan_poly_dimensions: dict):
        poly_width_percent_adjust = get_config_value(config, 'algorithm.poly_width_percent_adjustment', float)
        scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                              **scan_poly_dimensions)
        if poly_width_percent_adjust != 0.0:
            scan_poly = self._reduce_poly_width(poly=scan_poly,
                                                width_adjustment=poly_width_percent_adjust)
        return scan_poly

    def _should_show_algo(self, poly_data, poly_type, num_iterations, city_name) -> bool:
        display_algo = get_config_value(config, 'algo_display.show_display', bool)
        display_algo_city = get_config_value(config, 'algo_display.show_poly_finalist_city', str)
        steps_to_show_scan_poly = get_config_value(config, 'algo_display.steps_to_show_scan_poly', int)
        steps_to_show_poly_finalist = get_config_value(config, 'algo_display.steps_to_show_poly_finalist', int)

        if not display_algo or city_name != display_algo_city or not poly_data['show_algo']:
            return False

        if poly_type == 'scan_poly' and num_iterations % steps_to_show_scan_poly != 0:
            return False

        if poly_type == 'poly_finalist' and num_iterations % steps_to_show_poly_finalist != 0:
            return False

        if display_algo_city not in (city_name, 'N/A'):
            return False

        return True

    def find_best_poly_around_point(self, scan_poly_dimensions: dict, center_coord, city_name: str):
        search_height = get_config_value(config, 'algorithm.search_height', float)
        search_width = get_config_value(config, 'algorithm.search_width', float)
        search_steps = get_config_value(config, 'algorithm.search_steps', int)
        show_pause = get_config_value(config, 'algo_display.show_pause', float)

        scan_poly = self._create_scan_poly(scan_poly_dimensions)

        search_area_poly = poly_creation.create_poly(poly_type='rectangle',
                                                     center_coord=center_coord,
                                                     poly_height=search_height,
                                                     poly_width=search_width)

        search_area_patch = self.algo_map_creator.add_poly_to_map(poly=search_area_poly,
                                                                  show_pause=show_pause,
                                                                  **self._lookup_poly_characteristics(
                                                                      poly_type='search_area'))
        best_poly = None
        most_recent_scan_patch = None
        intersecting_patches = []
        poly_finalist_patches = []

        for poly, poly_type, num_iterations in self.rtree_analyzer.find_best_poly_around_point(
                scan_poly=scan_poly,
                search_area_poly=search_area_poly,
                search_steps=search_steps):

            poly_data = self._lookup_poly_characteristics(poly_type='best_poly')

            if not self._should_show_algo(poly_data=poly_data,
                                         poly_type=poly_type,
                                         num_iterations=num_iterations,
                                         city_name=city_name):
                self.algo_map_creator.disable()

            if poly_type in ('scan_poly', 'best_poly'):
                if most_recent_scan_patch:
                    self.algo_map_creator.remove_patch_from_map(most_recent_scan_patch)
                for i_patch in intersecting_patches:
                    self.algo_map_creator.remove_patch_from_map(i_patch)

            if poly_type == 'best_poly':
                for poly_finalist_patch in poly_finalist_patches:
                    self.algo_map_creator.remove_patch_from_map(patch=poly_finalist_patch)
                best_poly = poly
                logging.info("Found best polygon.")
                """
                if self._scan_poly_outside_of_search_area(scan_poly=poly,
                                                          search_area_poly=search_area_poly):
                    raise ValueError("Scan poly is outside of the search area. Increase the search dimensions.")
                """
                break

            patch = self.algo_map_creator.add_poly_to_map(poly=poly,
                                                          show_pause=show_pause,
                                                          **poly_data)

            # Load patch into appropriate scan history
            if poly_type == 'scan_poly':
                most_recent_scan_patch = patch
            elif poly_type == 'intersecting':
                intersecting_patches.append(patch)
            elif poly_type == 'poly_finalist':
                poly_finalist_patches.append(patch)

            self.algo_map_creator.enable()

        # We have found the best poly
        poly_data = self._lookup_poly_characteristics(poly_type='best_poly')
        self.algo_map_creator.add_poly_to_map(poly=best_poly,
                                              **poly_data)
        self.rtree_analyzer.add_poly(poly=best_poly,
                                     poly_class='text')
        self.algo_map_creator.remove_patch_from_map(patch=search_area_patch)

        self.algo_map_creator.enable()

        return best_poly
