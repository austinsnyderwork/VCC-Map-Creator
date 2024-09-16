import configparser

from . import poly_result
from .helper_functions import get_config_value, reduce_poly_width
import poly_creation
from poly_management import ScanPolyIntersectionsManager, TypedPolygon
from shapely import Polygon


config = configparser.ConfigParser()
config.read('config.ini')


def _create_scan_steps(text_box_dimensions: dict, scan_area_poly: TypedPolygon) -> tuple[list, list]:
    search_steps = get_config_value(config, 'algorithm.search_steps', int)
    scan_area_x_min, scan_area_y_min, scan_area_x_max, scan_area_y_max = scan_area_poly.bounds

    scan_poly_x_len = text_box_dimensions['x_max'] - text_box_dimensions['x_min']
    scan_poly_y_len = text_box_dimensions['y_max'] - text_box_dimensions['y_min']

    # Iterating steps through
    maximum_x_min = scan_area_x_max - scan_poly_x_len
    x_min_change = (maximum_x_min - scan_area_x_min) / search_steps
    x_min_steps = []
    for step in list(range(search_steps + 1)):
        step_distance = x_min_change * step
        x_min_steps.append(scan_area_x_min + step_distance)

    maximum_y_min = scan_area_y_max - scan_poly_y_len
    y_min_change = (maximum_y_min - scan_area_y_min) / search_steps
    y_min_steps = []
    for step in list(range(search_steps + 1)):
        step_distance = y_min_change * step
        y_min_steps.append(scan_area_y_min + step_distance)
    return x_min_steps, y_min_steps


class CityTextBoxSearch:

    def __init__(self, text_box_dimensions, city_poly: Polygon):
        self.text_box_dimensions = text_box_dimensions
        self.city_poly = city_poly
        self.city_coord = city_poly.centroid.x, city_poly.centroid.y

        self.poly_groups_manager = None

    def _create_scan_poly(self, text_box_dimensions: dict) -> TypedPolygon:
        poly_width_percent_adjust = get_config_value(config, 'algorithm.poly_width_percent_adjustment', float)
        scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                              **text_box_dimensions)
        if poly_width_percent_adjust != 0.0:
            scan_poly = reduce_poly_width(poly=scan_poly,
                                          width_adjustment=poly_width_percent_adjust)
        t_scan_poly = TypedPolygon(poly=scan_poly,
                                   poly_type='text')
        return t_scan_poly

    def _create_scan_area_poly(self, max_text_distance_to_city: int):
        x_dist = self.text_box_dimensions['x_max'] - self.text_box_dimensions['x_min']
        y_dist = self.text_box_dimensions['y_max'] - self.text_box_dimensions['y_min']
        center_x_coord = self.text_box_dimensions['x_min'] + x_dist/2
        center_y_coord = self.text_box_dimensions['y_min'] + y_dist/2
        center_coord = (center_x_coord, center_y_coord)
        search_height = (y_dist + max_text_distance_to_city) * 2
        search_width = (x_dist + max_text_distance_to_city) * 2
        search_area_poly = poly_creation.create_poly(poly_type='rectangle',
                                                     center_coord=center_coord,
                                                     poly_height=search_height,
                                                     poly_width=search_width)
        t_search_area_poly = TypedPolygon(poly=search_area_poly,
                                          poly_type='search_area',
                                          center_coord=center_coord)
        return t_search_area_poly

    def _run_initial_scan(self, x_steps: list, y_steps: list):
        text_x_len = self.text_box_dimensions['x_max'] - self.text_box_dimensions['x_min']
        text_y_len = self.text_box_dimensions['y_max'] - self.text_box_dimensions['y_min']

        num_iterations = 0
        for x_min, y_min in zip(x_steps, y_steps):
            x_max = x_min + text_x_len
            y_max = y_min + text_y_len
            scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                                  x_min=x_min,
                                                  y_min=y_min,
                                                  x_max=x_max,
                                                  y_max=y_max)
            scan_poly = TypedPolygon(poly=scan_poly,
                                     poly_type='text')
            result = poly_result.PolyResult(poly=scan_poly,
                                            poly_type='scan_poly',
                                            num_iterations=num_iterations)
            yield result

            intersecting_polys = self._get_intersecting_polys(scan_poly=scan_poly,
                                                              ignore_polys=[point_poly])
            invalid_polys = [poly for poly in intersecting_polys if poly.poly_type in ['scatter', 'text']]
            if len(invalid_polys) > 0:
                continue
            poly_group = PolyGroup(scan_poly=scan_poly,
                                   intersecting_polys=intersecting_polys)
            poly_groups_manager.add_poly_group(poly_group)

            num_intersections = len(intersecting_polys)
            if num_intersections not in poly_groups_dict:
                poly_groups_dict[num_intersections] = []

            poly_groups_dict[num_intersections].append(poly_group)
            for poly in intersecting_polys:
                result = poly_result.PolyResult(poly=poly,
                                                poly_type='intersecting',
                                                num_iterations=num_iterations)
                yield result

            num_iterations += 1

    def find_best_poly(self):
        max_text_distance_to_city = get_config_value(config, 'algorithm.maximum_distance_to_city', int)

        scan_area_poly = self._create_scan_area_poly(max_text_distance_to_city=max_text_distance_to_city)
        yield scan_area_poly, 'scan_area_poly'
        x_min_steps, y_min_steps = _create_scan_steps(text_box_dimensions=self.text_box_dimensions,
                                                      scan_area_poly=scan_area_poly)
        scan_poly_intersections_manager = ScanPolyIntersectionsManager()
