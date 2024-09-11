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
                                                  show_algo=show_line,
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
                                                  show_algo=show_scatter,
                                                  color=scatter_color,
                                                  transparency=scatter_transparency,
                                                  immediately_remove=immediately_remove_scatter)

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

    def find_best_poly_around_point(self, scan_poly_dimensions: dict, center_coord, city_name: str):
        search_height = float(config['algorithm']['search_height'])
        search_width = float(config['algorithm']['search_width'])
        search_steps = int(config['algorithm']['search_steps'])
        show_pause = float(config['algo_display']['show_pause'])
        steps_to_show_scan_poly = int(config['algo_display']['steps_to_show_scan_poly'])
        steps_to_show_poly_finalist = int(config['algo_display']['steps_to_show_poly_finalist'])
        display_algo_city = config['algo_display']['show_poly_finalist_city']
        display_algo_city = True if display_algo_city in (city_name, 'N/A') else False
        poly_width_percent_adjust = float(config['algorithm']['poly_width_percent_adjustment'])

        if not display_algo_city:
            self.algo_map_creator.disable()

        scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                              **scan_poly_dimensions)
        search_area_poly = poly_creation.create_search_area_polygon(center_coord=center_coord,
                                                                    search_distance_height=search_height,
                                                                    search_distance_width=search_width)

        search_area_patch = self.algo_map_creator.add_poly_to_map(poly=search_area_poly,
                                                                  show_pause=show_pause,
                                                                  **self._lookup_poly_characteristics(
                                                                      poly_type='search_area'))
        best_poly = None
        most_recent_scan_patch = None
        intersecting_patches = []
        poly_finalist_patches = []
        if poly_width_percent_adjust != 0.0:
            scan_poly = self._reduce_poly_width(poly=scan_poly,
                                                width_adjustment=poly_width_percent_adjust)

        for poly, poly_type in self.rtree_analyzer.find_available_poly_around_point(scan_poly=scan_poly,
                                                                                    search_area_poly=search_area_poly,
                                                                                    search_steps=search_steps,
                                                                                    steps_to_show_scan_poly=steps_to_show_scan_poly,
                                                                                    steps_to_show_poly_finalist=steps_to_show_poly_finalist):

            poly_data = self._lookup_poly_characteristics(poly_type=poly_type)
            patch = self.algo_map_creator.add_poly_to_map(poly=poly,
                                                          show_pause=show_pause,
                                                          **poly_data)

            if poly_type == 'best_poly':
                if most_recent_scan_patch:
                    self.algo_map_creator.remove_patch_from_map(patch=most_recent_scan_patch)
                for poly_finalist_patch in poly_finalist_patches:
                    self.algo_map_creator.remove_patch_from_map(patch=poly_finalist_patch)
                best_poly = poly
                logging.info("Found best polygon.")
                break
            elif poly_type == 'scan_poly':
                if self._scan_poly_outside_of_search_area(scan_poly=poly,
                                                          search_area_poly=search_area_poly):
                    raise ValueError("Scan poly is outside of the search area. Increase the search dimensions.")
                if most_recent_scan_patch:
                    self.algo_map_creator.remove_patch_from_map(patch=most_recent_scan_patch)
                most_recent_scan_patch = patch

                for patch in intersecting_patches:
                    self.algo_map_creator.remove_patch_from_map(patch=patch)
            elif poly_type == 'intersecting':
                intersecting_patches.append(patch)
            elif poly_type == 'poly_finalist':
                poly_finalist_patches.append(patch)

            if not poly_data['show_algo']:
                continue

        poly_width_percent_adjust = float(config['algorithm']['poly_width_percent_adjustment'])
        best_poly = self._reduce_poly_width(poly=best_poly,
                                            width_adjustment=poly_width_percent_adjust)

        poly_data = self._lookup_poly_characteristics(poly_type='best_poly')
        self.algo_map_creator.add_poly_to_map(poly=best_poly,
                                              **poly_data)
        self.rtree_analyzer.add_poly(poly=best_poly,
                                     poly_class='text')
        self.algo_map_creator.remove_patch_from_map(patch=search_area_patch)

        self.algo_map_creator.enable()

        return best_poly
