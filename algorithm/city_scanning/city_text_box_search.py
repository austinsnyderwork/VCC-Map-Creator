import configparser
import logging
import numpy as np

from utils import get_config_value
import poly_creation
from algorithm.poly_management import TypedPolygon, ScanPolysManager
from algorithm import rtree_analyzer, spatial_analysis
from algorithm.algo_utils import poly_result
from algorithm.poly_management import ScanPoly

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


def _determine_nearby_polys(scan_polys: list[TypedPolygon], rtree_idx, polygons):
    nearby_poly_search_width = get_config_value(config, 'algorithm.nearby_poly_search_width', int)
    nearby_poly_search_height = get_config_value(config, 'algorithm.nearby_poly_search_height', int)

    num_iterations = 0
    for scan_poly in scan_polys:
        center_coord = scan_poly.poly.centroid.x, scan_poly.poly.centroid.y
        nearby_search_poly = poly_creation.create_poly(poly_type='rectangle',
                                                       center_coord=center_coord,
                                                       poly_width=nearby_poly_search_width,
                                                       poly_height=nearby_poly_search_height)
        nearby_search_poly = TypedPolygon(poly=nearby_search_poly,
                                          poly_type='nearby_search',
                                          poly_class='algorithm_misc')
        scan_poly.nearby_search_poly = nearby_search_poly

        nearby_polys = spatial_analysis.get_intersecting_polys(rtree_idx=rtree_idx,
                                                               polygons=polygons,
                                                               scan_poly=nearby_search_poly)
        scan_poly.nearby_polys = nearby_polys

        num_iterations += 1
    return scan_polys


class CityTextBoxSearch:

    def __init__(self, text_box_dimensions: dict, city_poly: TypedPolygon):
        self.text_box_dimensions = text_box_dimensions
        self.city_poly = city_poly
        self.city_coord = city_poly.centroid.x, city_poly.centroid.y
        self.city_name = city_poly.city_name

        self.scan_polys_manager = ScanPolysManager()

    @property
    def text_width_height(self):
        width = self.text_box_dimensions['x_max'] - self.text_box_dimensions['x_min']
        height = self.text_box_dimensions['y_max'] - self.text_box_dimensions['y_min']
        return width, height

    def _create_scan_poly(self, text_box_dimensions: dict) -> ScanPoly:
        from algorithm.algo_utils.helper_functions import reduce_poly_width
        poly_width_percent_adjust = get_config_value(config, 'algorithm.poly_width_percent_adjustment', float)
        scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                              **text_box_dimensions)
        if poly_width_percent_adjust != 0.0:
            scan_poly = reduce_poly_width(poly=scan_poly,
                                          width_adjustment=poly_width_percent_adjust)
        scan_poly = ScanPoly(poly=scan_poly,
                             poly_class='text',
                             city_name=self.city_name)
        return scan_poly

    def _create_initial_scan_area_poly(self):
        x_dist, y_dist = self.text_width_height
        center_coord = self.city_poly.centroid.x, self.city_poly.centroid.y
        search_height = (y_dist + 50) * 2
        search_width = (x_dist + 50) * 2
        scan_area_poly = poly_creation.create_poly(poly_type='rectangle',
                                                   center_coord=center_coord,
                                                   poly_height=search_height,
                                                   poly_width=search_width)
        t_scan_area_poly = TypedPolygon(poly=scan_area_poly,
                                        poly_class='algorithm_misc',
                                        poly_type='scan_area',
                                        center_coord=center_coord)
        return t_scan_area_poly

    def _run_initial_scan(self, x_min_steps: list, y_min_steps: list, rtree_idx, polygons):
        unacceptable_scan_overlap_classes = get_config_value(config, 'algorithm.unacceptable_scan_overlap_classes',
                                                             list)

        num_iterations = 0

        x_y_steps = [(x_min, y_min) for x_min in x_min_steps for y_min in y_min_steps]
        for x_min, y_min in x_y_steps:
            scan_poly_width, scan_poly_height = self.text_width_height
            x_max = x_min + scan_poly_width
            y_max = y_min + scan_poly_height
            scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                                  x_min=x_min,
                                                  y_min=y_min,
                                                  x_max=x_max,
                                                  y_max=y_max)
            scan_poly_obj = ScanPoly(poly=scan_poly,
                                     poly_class='algorithm_misc',
                                     city_name=self.city_name)
            intersecting_polys = spatial_analysis.get_intersecting_polys(rtree_idx=rtree_idx,
                                                                         polygons=polygons,
                                                                         scan_poly=scan_poly_obj)
            scan_poly_obj.intersecting_polys = intersecting_polys
            scan_result = poly_result.PolyResult(poly=scan_poly_obj,
                                                 poly_type='scan',
                                                 num_iterations=num_iterations)

            non_starter_polys = [poly for poly in intersecting_polys if
                                 poly.poly_class in unacceptable_scan_overlap_classes]
            if len(non_starter_polys) > 0:
                continue

            yield scan_result

            for poly in intersecting_polys:
                result = poly_result.PolyResult(poly=poly,
                                                poly_type='intersecting',
                                                num_iterations=num_iterations)
                yield result

            self.scan_polys_manager.add_scan_poly(scan_poly_obj)

            num_iterations += 1

    def _determine_best_poly_finalist(self, finalist_scan_polys: list[ScanPoly]):
        least_nearby_polys = 100
        best_scan_poly = finalist_scan_polys[0]
        for scan_poly in finalist_scan_polys[1:]:
            if len(scan_poly.nearby_polys) < least_nearby_polys:
                least_nearby_polys = len(scan_poly.nearby_polys)
                best_scan_poly = scan_poly
            elif scan_poly.score == best_scan_poly.score:
                if scan_poly.score > best_scan_poly.score:
                    best_scan_poly = scan_poly
        logging.info(f"Score best poly: {best_scan_poly.score}")
        return best_scan_poly

    def _create_text_boxes_surrounding_city_poly(self) -> list[ScanPoly]:
        city_buffer = get_config_value(config, 'algorithm.city_to_text_box_buffer', int)
        num_steps = get_config_value(config, 'algorithm.search_steps', int)

        poly_coords = self.city_poly.bounds
        poly_coords = [poly_coord + city_buffer for poly_coord in poly_coords]
        city_min_x, city_min_y, city_max_x, city_max_y = poly_coords

        text_width, text_height = self.text_width_height

        x_min_steps = np.linspace(city_min_x - text_width,
                                  city_max_x,
                                  num_steps)
        y_min_steps = np.linspace(city_min_y,
                                  city_max_y,
                                  num_steps)

        polys = []
        # top steps
        top_y = city_max_y + text_height
        bottom_y = city_max_y
        for x_min in x_min_steps:
            top_poly = self._create_scan_poly({
                'x_min': x_min,
                'y_min': bottom_y,
                'x_max': x_min + text_width,
                'y_max': top_y
            })
            polys.append(top_poly)

        # bottom steps
        top_y = city_min_y
        bottom_y = city_min_y - text_height
        for x_min in x_min_steps:
            bottom_poly = self._create_scan_poly({
                'x_min': x_min,
                'y_min': bottom_y,
                'x_max': x_min + text_width,
                'y_max': top_y
            })
            polys.append(bottom_poly)

        # left steps
        left_x = city_min_x - text_width
        right_x = city_min_x
        for y_min in y_min_steps:
            left_poly = self._create_scan_poly({
                'x_min': left_x,
                'y_min': y_min,
                'x_max': right_x,
                'y_max': y_min + text_height
            })
            polys.append(left_poly)

        # right steps
        left_x = city_max_x
        right_x = city_max_x + text_width
        for y_min in y_min_steps:
            left_poly = self._create_scan_poly({
                'x_min': left_x,
                'y_min': y_min,
                'x_max': right_x,
                'y_max': y_min + text_height
            })
            polys.append(left_poly)
        return polys

    def _get_intersecting_polygons_for_scan_polys(self, scan_polys: list[ScanPoly], rtree_idx, polygons: dict):
        unacceptable_scan_overlap_classes = get_config_value(config, 'algorithm.unacceptable_scan_overlap_classes',
                                                             list)
        for num_iterations, scan_poly in enumerate(scan_polys):
            intersecting_polys = spatial_analysis.get_intersecting_polys(rtree_idx=rtree_idx,
                                                                         polygons=polygons,
                                                                         scan_poly=scan_poly,
                                                                         attributes_of_polys_to_ignore={
                                                                             'city_name': self.city_name
                                                                         })
            non_starter_polys = [poly for poly in intersecting_polys if
                                 poly.poly_class in unacceptable_scan_overlap_classes]
            if len(non_starter_polys) > 0:
                continue

            scan_result = poly_result.PolyResult(poly=scan_poly,
                                                 poly_type='scan',
                                                 num_iterations=num_iterations)
            yield scan_result
            scan_poly.intersecting_polys = intersecting_polys

            for poly in intersecting_polys:
                intersect_result = poly_result.PolyResult(poly=poly,
                                                          poly_type='intersecting',
                                                          num_iterations=num_iterations)
                yield intersect_result

            self.scan_polys_manager.add_scan_poly(scan_poly)

    def find_best_poly(self, rtree_analyzer_: rtree_analyzer.RtreeAnalyzer):
        unacceptable_scan_overlap_classes = get_config_value(config, 'algorithm.unacceptable_scan_overlap_classes',
                                                             list)

        scan_polys = self._create_text_boxes_surrounding_city_poly()
        for i, scan_poly in enumerate(scan_polys):
            scan_result = poly_result.PolyResult(poly=scan_poly,
                                                 poly_type='scan',
                                                 num_iterations=i)
            yield scan_result
        for result in self._get_intersecting_polygons_for_scan_polys(scan_polys=scan_polys,
                                                                     rtree_idx=rtree_analyzer_.rtree_idx,
                                                                     polygons=rtree_analyzer_.polygons):
            yield result

        best_scan_polys = self.scan_polys_manager.get_least_intersections_poly_groups(
            poly_types_to_omit=unacceptable_scan_overlap_classes,
            poly_attributes_to_omit={
                'city_name': self.city_name,
                'outpatient': self.city_name,
                'origin': self.city_name
            })

        poly_with_most_space = best_scan_polys[0]
        greatest_distance = -1
        for i, best_scan_poly in enumerate(best_scan_polys):
            finalist_result = poly_result.PolyResult(poly=best_scan_poly,
                                                     poly_type='finalist',
                                                     num_iterations=i)
            yield finalist_result
            closest_distance, closest_polys = rtree_analyzer_.get_closest_polygons(
                query_poly=best_scan_poly,
                attributes_to_omit={'city_name': self.city_name})
            logging.info(f"Closest distance for poly finalist: {closest_distance}")
            if i == 0:
                poly_with_most_space = best_scan_poly
                greatest_distance = closest_distance
            else:
                if closest_distance > greatest_distance:
                    greatest_distance = closest_distance
                    poly_with_most_space = best_scan_poly
        best_result = poly_result.PolyResult(poly=poly_with_most_space,
                                             poly_type='best',
                                             num_iterations=-1)
        yield best_result
        
