import configparser
import math

import poly_creation
from utils.helper_functions import get_config_value

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

def lookup_poly_characteristics(self, poly_type: str):
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

def should_show_algo(poly_data, poly_type, num_iterations, city_name) -> bool:
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

