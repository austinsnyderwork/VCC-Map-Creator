import logging
import numpy as np

from utils import get_config_value
from polygons import polygon_factory, typed_polygon
from algorithm import rtree_analyzer, spatial_analysis
from algorithm.algo_utils import poly_result
import config_manager
from polygons import polygon_factory, scan_polygons_manager
from things import box_geometry
from things.visualization_elements import visualization_elements


def _move_text_box_to_bottom_left_city_box_corner(text_box: box_geometry.BoxGeometry, city_box: box_geometry.BoxGeometry):
    x_distance = city_box.width + (text_box.x_max - city_box.x_max)
    y_distance = city_box.height - (text_box.y_max - city_box.y_max)
    text_box.move_box('left', x_distance)
    text_box.move_box('down', y_distance)

class CityScanner:

    def __init__(self, config: config_manager.ConfigManager, text_box: box_geometry.BoxGeometry,
                 city_scatter_element: visualization_elements.CityScatter):
        self.config = config
        self.text_box = text_box
        self.city_scatter_element = city_scatter_element

        self.scan_polys_manager = scan_polygons_manager.ScanPolygonsManager()

        self.remove_polys_by_type = {
            'scan': ['scan', 'intersecting'],
            'finalist': ['scan', 'intersecting', 'finalist', 'nearby_search'],
            'best': ['scan', 'intersecting', 'finalist', 'nearby_search']
        }

        self.poly_patches = {
            'best': None,
            'nearby_search': None,
            'scan': None,
            'finalist': None,
            'intersecting': []
        }

    def _create_initial_scan_area_poly(self, search_height: int, search_width: int):
        city_poly = self.city_scatter_element.algorithm_poly
        center_coord = city_poly.centroid.x, city_poly.centroid.y
        scan_area_poly = poly_creation.create_poly(poly_type='rectangle',
                                                   center_coord=center_coord,
                                                   poly_height=search_height,
                                                   poly_width=search_width)
        t_scan_area_poly = TypedPolygon(poly=scan_area_poly,
                                        poly_class='algorithm_misc',
                                        poly_type='scan_area',
                                        center_coord=center_coord)
        return t_scan_area_poly

    def _run_initial_scan(self, number_of_steps: int, rtree_idx, polygons, city_buffer: int,
                          unacceptable_scan_overlap_classes: list[str]):
        scan_polygons = self._create_polygons_surrounding_city(city_buffer=city_buffer,
                                                               number_of_steps=number_of_steps)
        for scan_polygon in scan_polygons:
            intersecting_polygons = spatial_analysis.get_interscting_polygons(rtree_idx=rtree_idx,
                                                                              polygons=polygons,
                                                                              scan_poly=scan_polygon)
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
            scan_poly_obj = typed_polygon.ScanPolygon(poly=scan_poly,
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

    def _determine_best_poly_finalist(self, finalist_scan_polys: list[visualization_elements.TextBoxScan]):
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

    def _create_polygons_surrounding_city(self, city_buffer: int, number_of_steps: int) -> list[visualization_elements.TextBoxScan]:

        city_box: box_geometry.BoxGeometry = self.city_scatter_element.algorithm_box_geometry
        city_box.add_buffer(city_buffer)
        _move_text_box_to_bottom_left_city_box_corner(text_box=self.text_box,
                                                      city_box=city_box)
        city_perimeter = (2 * city_box.height) + (2 * city_box.width)
        perimeter_movement_amount = city_perimeter / number_of_steps

        while self.text_box.x_min < city_box.x_max:
            scan_poly = polygon_factory.create_poly(poly_type=typed_polygon.ScanPolygon,
                                                    kwargs=self.text_box.dimensions)
            self.text_box.move_box('right', min(perimeter_movement_amount, (city_box.x_max - self.text_box.x_min)))
            yield scan_poly

        while self.text_box.y_min < city_box.y_max:
            scan_poly = polygon_factory.create_poly(poly_type=typed_polygon.ScanPolygon,
                                                    kwargs=self.text_box.dimensions)
            self.text_box.move_box('up', min(perimeter_movement_amount, (city_box.y_max - self.text_box.y_min)))
            yield scan_poly

        while self.text_box.x_max > city_box.x_min:
            scan_poly = polygon_factory.create_poly(poly_type=typed_polygon.ScanPolygon,
                                                    kwargs=self.text_box_dimensions)
            self.text_box.move_box('left', min(perimeter_movement_amount, (self.text_box.x_max - city_box.x_min)))
            yield scan_poly

        while self.text_box.y_max > city_box.y_min:
            scan_poly = polygon_factory.create_poly(poly_type=typed_polygon.ScanPolygon,
                                                    kwargs=self.text_box_dimensions)
            self.text_box.move_box('down', min(perimeter_movement_amount, (self.text_box.y_max - city_box.y_min)))
            yield scan_poly
        return polys

    def _get_intersecting_polygons_for_scan_polys(self, scan_polys: list[visualization_elements.TextBoxScan], rtree_idx, polygons: dict):
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

        best_scan_polys = self.scan_polys_manager.get_least_intersecting_scan_polygons(
            poly_types_to_omit=unacceptable_scan_overlap_classes,
            poly_attributes_to_omit={
                'city_name': self.city_name,
                'visiting': self.city_name,
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
        
