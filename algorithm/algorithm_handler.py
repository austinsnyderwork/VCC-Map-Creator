import configparser
from shapely.geometry import Polygon

from interfacing import VisualizationElement
from utils.helper_functions import get_config_value
from . import algorithm_map_creator, rtree_analyzer
from .city_text_box_search import CityTextBoxSearch
from .algo_utils import helper_functions
import poly_creation
from .poly_management import TypedPolygon

config = configparser.ConfigParser()
config.read('config.ini')


def verify_poly_validity(poly, name):
    if not poly.is_valid:
        raise ValueError(f"{name} poly was invalid on creation.")


def reduce_poly_width(poly, width_adjustment: float):
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


def lookup_poly_characteristics(poly_type: str):
    poly_type_data = {
        'search_area_poly': {
            'color': get_config_value(config, 'algo_display.search_area_poly_color', str),
            'transparency': get_config_value(config, 'algo_display.search_area_poly_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_search_area_poly', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_search_area_poly', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_search_area_poly', bool)
        },
        'scan_poly': {
            'color': get_config_value(config, 'algo_display.scan_poly_color', str),
            'transparency': get_config_value(config, 'algo_display.scan_poly_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_scan_poly', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_scan_poly', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_scan_poly', bool)
        },
        'intersecting': {
            'color': get_config_value(config, 'algo_display.intersecting_poly_color', str),
            'transparency': get_config_value(config, 'algo_display.intersecting_poly_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_intersecting_poly', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_intersecting_poly', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_intersecting_poly', bool)
        },
        'best_poly': {
            'color': get_config_value(config, 'algo_display.best_poly_color', str),
            'transparency': get_config_value(config, 'algo_display.best_poly_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_best_poly', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_best_poly', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_best_poly', bool)
        },
        'poly_finalist': {
            'color': get_config_value(config, 'algo_display.poly_finalist_color', str),
            'transparency': get_config_value(config, 'algo_display.poly_finalist_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_poly_finalist', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_poly_finalist', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_poly_finalist', bool)
        },
        'nearby_search': {
            'color': get_config_value(config, 'algo_display.nearby_search_poly_color', str),
            'transparency': get_config_value(config, 'algo_display.nearby_search_poly_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_nearby_search_poly', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_nearby_search_poly', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_nearby_search_poly', bool)
        }
    }

    return poly_type_data[poly_type]


def should_show_algo(poly_data, poly_type, city_name, new_max_score: bool = False, num_iterations: int = None) -> bool:
    display_algo = get_config_value(config, 'algo_display.show_display', bool)
    display_algo_city = get_config_value(config, 'algo_display.show_poly_finalist_city', str)
    steps_to_show_scan_poly = get_config_value(config, 'algo_display.steps_to_show_scan_poly', int)
    steps_to_show_poly_finalist = get_config_value(config, 'algo_display.steps_to_show_poly_finalist', int)

    if not display_algo or display_algo_city not in (city_name, 'N/A') or not poly_data['show_algo']:
        return False
    elif new_max_score:
        return True

    if poly_type in ('scan_poly', 'intersecting') and num_iterations % steps_to_show_scan_poly != 0:
        return False

    if poly_type in ('poly_finalist', 'nearby_search') and num_iterations % steps_to_show_poly_finalist != 0:
        return False

    if display_algo_city not in (city_name, 'N/A'):
        return False

    return True


class AlgorithmHandler:

    def __init__(self):
        show_algo_display = False if config['algo_display']['show_display'] == 'False' else True
        self.algo_map_creator = algorithm_map_creator.AlgorithmMapCreator(show_display=show_algo_display)
        self.rtree_analyzer = rtree_analyzer.RtreeAnalyzer()

    def plot_lines(self, line_eles: list[VisualizationElement]):
        line_color = get_config_value(config, 'algo_display.line_color', str)
        show_line = get_config_value(config, 'algo_display.show_line', bool)
        line_transparency = get_config_value(config, 'algo_display.line_transparency', float)
        immediately_remove_line = get_config_value(config, 'algo_display.immediately_remove_line', bool)

        t_polys = []
        for line_ele in line_eles:
            poly = poly_creation.create_poly(poly_type='line', x_data=line_ele.x_data, y_data=line_ele.y_data,
                                             line_width=line_ele.line_width)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='line poly')
            t_poly = TypedPolygon(poly=poly,
                                  poly_type='line',
                                  origin=line_ele.origin,
                                  outpatient=line_ele.outpatient)
            t_polys.append(t_poly)
            self.rtree_analyzer.add_poly(poly_class='line',
                                         poly=t_poly)
            self.algo_map_creator.add_poly_to_map(poly=poly,
                                                  show_algo=show_line,
                                                  color=line_color,
                                                  transparency=line_transparency,
                                                  immediately_remove=immediately_remove_line)
        return t_polys

    def plot_points(self, scatter_eles: list[VisualizationElement]):
        scatter_size = get_config_value(config, 'dimensions.scatter_size', float)
        units_radius_per_1_scatter_size = get_config_value(config, 'dimensions.units_radius_per_1_scatter_size', float)

        scatter_color = get_config_value(config, 'algo_display.scatter_color', str)
        show_scatter = get_config_value(config, 'algo_display.show_scatter', bool)
        scatter_transparency = get_config_value(config, 'algo_display.scatter_transparency', float)
        immediately_remove_scatter = get_config_value(config, 'algo_display.immediately_remove_scatter', bool)
        t_polys = []
        for scatter_ele in scatter_eles:
            units_radius = scatter_size * units_radius_per_1_scatter_size
            poly = poly_creation.create_poly(poly_type='scatter', center=scatter_ele.coord, radius=units_radius)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='scatter poly')
            t_poly = TypedPolygon(poly=poly,
                                  poly_type='scatter',
                                  city_name=scatter_ele.city_name)
            t_polys.append(t_poly)
            scatter_ele.add_value('city_poly', value=t_poly)
            self.rtree_analyzer.add_poly(poly_class='scatter',
                                         poly=t_poly)
            self.algo_map_creator.add_poly_to_map(poly=t_poly,
                                                  show_algo=show_scatter,
                                                  color=scatter_color,
                                                  transparency=scatter_transparency,
                                                  immediately_remove=immediately_remove_scatter)
        return t_polys

    def _create_scan_poly(self, scan_poly_dimensions: dict) -> TypedPolygon:
        poly_width_percent_adjust = get_config_value(config, 'algorithm.poly_width_percent_adjustment', float)
        scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                              **scan_poly_dimensions)
        if poly_width_percent_adjust != 0.0:
            scan_poly = helper_functions.reduce_poly_width(poly=scan_poly,
                                                           width_adjustment=poly_width_percent_adjust)
        t_scan_poly = TypedPolygon(poly=scan_poly,
                                   poly_type='text')
        return t_scan_poly

    def _create_search_area_poly(self, scan_poly: Polygon, max_text_distance_to_city: int):
        x_min, y_min, x_max, y_max = scan_poly.bounds
        y_dist = y_max - scan_poly.centroid.y
        x_dist = x_max - scan_poly.centroid.x
        search_height = (y_dist + max_text_distance_to_city) * 2
        search_width = (x_dist + max_text_distance_to_city) * 2

        center_coord = scan_poly.centroid.x, scan_poly.centroid.y
        search_area_poly = poly_creation.create_poly(poly_type='rectangle',
                                                     center_coord=center_coord,
                                                     poly_height=search_height,
                                                     poly_width=search_width)
        t_search_area_poly = TypedPolygon(poly=search_area_poly,
                                          center_coord=(scan_poly.centroid.x, scan_poly.centroid.y))
        return t_search_area_poly

    def _handle_city_text_box_search(self, city_text_box_search: CityTextBoxSearch) -> TypedPolygon:
        poly_patches = {
            'best_poly': None,
            'nearby_search': None,
            'scan': None,
            'poly_finalist': None,
            'intersecting': []
        }

        remove_polys_by_type = {
            'scan_poly': ['scan', 'intersecting'],
            'poly_finalist': ['scan', 'intersecting', 'poly_finalist', 'nearby_search'],
            'best_poly': ['scan', 'intersecting', 'poly_finalist', 'nearby_search']
        }
        show_pause = get_config_value(config, 'algo_display.show_pause', float)
        extra_pause_for_new_max_score = get_config_value(config, 'algo_display.extra_pause_for_new_max_score', int)

        for result in city_text_box_search.find_best_poly(rtree_idx=self.rtree_analyzer.rtree_idx,
                                                          polygons=self.rtree_analyzer.polygons):
            poly_data = lookup_poly_characteristics(poly_type=result.poly_type)
            show_algo_for_poly = should_show_algo(poly_data=poly_data,
                                                  poly_type=result.poly_type,
                                                  num_iterations=result.num_iterations,
                                                  city_name=city_text_box_search.city_name,
                                                  new_max_score=result.new_max_score)
            if not show_algo_for_poly:
                self.algo_map_creator.disable()
            else:
                if result.poly_type in remove_polys_by_type:
                    polys_to_remove = remove_polys_by_type[result.poly_type]
                    for remove_poly_type in polys_to_remove:
                        if remove_poly_type == 'intersecting':
                            if len(poly_patches['intersecting']) > 0:
                                for idx in reversed(range(len(poly_patches['intersecting']))):
                                    i_patch = poly_patches['intersecting'][idx - 1]
                                    self.algo_map_creator.remove_patch_from_map(i_patch)
                                    poly_patches['intersecting'].pop(idx - 1)
                        elif poly_patches[remove_poly_type]:
                            self.algo_map_creator.remove_patch_from_map(poly_patches[remove_poly_type])
                            poly_patches[remove_poly_type] = None

                temp_show_pause = show_pause
                if result.new_max_score:
                    temp_show_pause = show_pause + extra_pause_for_new_max_score
                patch = self.algo_map_creator.add_poly_to_map(poly=result.poly,
                                                              show_pause=temp_show_pause,
                                                              **poly_data)
                # Load patch into appropriate scan history
                if patch:
                    if result.poly_type == 'scan_poly':
                        poly_patches['scan'] = patch
                    if result.poly_type == 'nearby_search':
                        poly_patches['nearby_search'] = patch
                    elif result.poly_type == 'intersecting':
                        poly_patches['intersecting'].append(patch)
                    elif result.poly_type == 'poly_finalist':
                        poly_patches['poly_finalist'] = patch
                    elif result.poly_type == 'best_poly':
                        poly_patches['best_poly'] = patch

            if result.poly_type == 'best_poly':
                return result.poly

    def find_best_polys(self, city_elements: list[VisualizationElement]):
        city_text_box_search_objs = []
        for city_ele in city_elements:
            text_box_dimensions = city_ele.text_box_element.dimensions
            city_text_box_search = CityTextBoxSearch(text_box_dimensions=text_box_dimensions,
                                                     city_poly=city_ele.city_poly,
                                                     city_name=city_ele.city_name)
            city_text_box_search_objs.append(city_text_box_search)

        for city_text_box_search in city_text_box_search_objs:
            best_poly = self._handle_city_text_box_search(city_text_box_search=city_text_box_search)

            poly_data = lookup_poly_characteristics(poly_type='best_poly')
            self.algo_map_creator.add_poly_to_map(poly=best_poly,
                                                  **poly_data)
            self.rtree_analyzer.add_poly(poly=best_poly,
                                         poly_class='text')
