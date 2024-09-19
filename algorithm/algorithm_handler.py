import configparser
import logging

from . import algorithm_map_creator, rtree_analyzer
from .city_scanning import city_angles_tracker
from interfacing import VisualizationElement
from utils.helper_functions import get_config_value
from algorithm.city_scanning.city_text_box_search import CityTextBoxSearch
from .algo_utils import helper_functions
import poly_creation
from .poly_management import TypedPolygon

config = configparser.ConfigParser()
config.read('config.ini')


def lookup_poly_characteristics(poly_type: str):
    poly_type_data = {
        'scan_area': {
            'color': get_config_value(config, 'algo_display.search_area_poly_color', str),
            'transparency': get_config_value(config, 'algo_display.search_area_poly_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_search_area_poly', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_search_area_poly', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_search_area_poly', bool)
        },
        'scan': {
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
        'best': {
            'color': get_config_value(config, 'algo_display.best_poly_color', str),
            'transparency': get_config_value(config, 'algo_display.best_poly_transparency', float),
            'show_algo': get_config_value(config, 'algo_display.show_best_poly', bool),
            'immediately_remove': get_config_value(config, 'algo_display.immediately_remove_best_poly', bool),
            'should_plot': False,
            'center_view': get_config_value(config, 'algo_display.center_view_on_best_poly', bool)
        },
        'finalist': {
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


def should_show_algo(poly_data, poly_type, city_name, new_max_score: bool = False, num_iterations: int = None,
                     force_show: bool = False) -> bool:
    display_algo = get_config_value(config, 'algo_display.show_display', bool)
    display_algo_city = get_config_value(config, 'algo_display.show_poly_finalist_city', str)
    force_show_new_max_scores = get_config_value(config, 'algo_display.force_show_new_max_scores', bool)
    steps_to_show_scan_poly = get_config_value(config, 'algo_display.steps_to_show_scan_poly', int)
    steps_to_show_poly_finalist = get_config_value(config, 'algo_display.steps_to_show_poly_finalist', int)

    if force_show:
        logging.debug("Force show is true, so showing this poly.")
        return True

    if not display_algo or display_algo_city not in (city_name, 'N/A') or not poly_data['show_algo']:
        logging.debug(f"Display algo: {display_algo} | Display algo city: {display_algo_city} | "
                      f"Show algo for poly specifically: {poly_data['show_algo']}. Showing poly.")
        return False
    elif force_show_new_max_scores and new_max_score:
        return True

    if poly_type in ('scan', 'intersecting') and num_iterations % steps_to_show_scan_poly != 0:
        return False

    if poly_type in ('finalist', 'nearby_search') and num_iterations % steps_to_show_poly_finalist != 0:
        logging.debug(f"poly_type: {poly_type} | num_iterations: {num_iterations}. Showing poly.")
        return False

    if display_algo_city not in (city_name, 'N/A'):
        return False

    logging.debug("No other conditions met. Displaying poly.")
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
                                  poly_class='line',
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
                                  poly_class='scatter',
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

    def _handle_city_text_box_search(self, city_text_box_search: CityTextBoxSearch) -> TypedPolygon:
        poly_patches = {
            'best': None,
            'nearby_search': None,
            'scan': None,
            'finalist': None,
            'intersecting': []
        }

        remove_polys_by_type = {
            'scan': ['scan', 'intersecting'],
            'finalist': ['scan', 'intersecting', 'finalist', 'nearby_search'],
            'best': ['scan', 'intersecting', 'finalist', 'nearby_search']
        }
        show_pause = get_config_value(config, 'algo_display.show_pause', float)
        extra_pause_for_new_max_score = get_config_value(config, 'algo_display.extra_pause_for_new_max_score', int)
        extra_pause_for_force_show = get_config_value(config, 'algo_display.extra_pause_for_force_show', int)

        for result in city_text_box_search.find_best_poly(rtree_idx=self.rtree_analyzer.rtree_idx,
                                                          polygons=self.rtree_analyzer.polygons):
            poly_data = lookup_poly_characteristics(poly_type=result.poly_type)
            show_algo_for_poly = should_show_algo(poly_data=poly_data,
                                                  poly_type=result.poly_type,
                                                  num_iterations=result.num_iterations,
                                                  city_name=city_text_box_search.city_name,
                                                  new_max_score=result.new_max_score,
                                                  force_show=result.force_show)
            if show_algo_for_poly:
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
                if result.force_show:
                    temp_show_pause = temp_show_pause + extra_pause_for_force_show
                patch = self.algo_map_creator.add_poly_to_map(poly=result.poly,
                                                              show_pause=temp_show_pause,
                                                              **poly_data)
                # Load patch into appropriate scan history
                if patch:
                    if result.poly_type == 'scan':
                        poly_patches['scan'] = patch
                    if result.poly_type == 'nearby_search':
                        poly_patches['nearby_search'] = patch
                    elif result.poly_type == 'intersecting':
                        poly_patches['intersecting'].append(patch)
                    elif result.poly_type == 'finalist':
                        poly_patches['finalist'] = patch
                    elif result.poly_type == 'best':
                        poly_patches['best'] = patch

            if result.poly_type == 'best':
                return result.poly

    def find_best_polys(self, city_elements: list[VisualizationElement]):
        for city_ele in city_elements:
            logging.info(f"Finding best poly for {city_ele.city_name}")
            text_box_dimensions = city_ele.text_box_element.dimensions
            city_text_box_search = CityTextBoxSearch(text_box_dimensions=text_box_dimensions,
                                                     city_poly=city_ele.city_poly)
            best_poly = self._handle_city_text_box_search(city_text_box_search=city_text_box_search)
            logging.info(f"Found best poly for {city_ele.city_name}.")
            city_ele.best_poly = best_poly

            poly_data = lookup_poly_characteristics(poly_type='best')
            show_poly = should_show_algo(poly_data=poly_data,
                                         poly_type='best',
                                         city_name=city_ele.city_name)
            if show_poly:
                self.algo_map_creator.add_poly_to_map(poly=best_poly,
                                                      **poly_data)
            self.rtree_analyzer.add_poly(poly=best_poly,
                                         poly_class='text')
