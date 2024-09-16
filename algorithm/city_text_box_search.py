import configparser

from .helper_functions import reduce_poly_width
from ..utils import get_config_value
import poly_creation
from poly_management import ScanPolysManager, ScanPoly, TypedPolygon
from rtree_analysis import RtreeAnalyzer
from . import scoring, spatial_analysis_functions, poly_result

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

    def __init__(self, text_box_dimensions: dict, city_poly: TypedPolygon, city_name: str):
        self.text_box_dimensions = text_box_dimensions
        self.city_poly = city_poly
        self.city_coord = city_poly.centroid.x, city_poly.centroid.y
        self.city_name = city_name

        self.scan_polys_manager = ScanPolysManager()

    @property
    def text_width_height(self):
        width = self.text_box_dimensions['x_max'] - self.text_box_dimensions['x_min']
        height = self.text_box_dimensions['y_max'] - self.text_box_dimensions['y_min']
        return width, height

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
        x_dist, y_dist = self.text_width_height
        center_x_coord = self.text_box_dimensions['x_min'] + x_dist / 2
        center_y_coord = self.text_box_dimensions['y_min'] + y_dist / 2
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

    def _run_initial_scan(self, x_min_steps: list, y_min_steps: list, rtree_idx):
        unacceptable_scan_overlap_types = get_config_value(config, 'algorithm.unacceptable_scan_overlap_types', list)

        num_iterations = 0
        for x_min, y_min in zip(x_min_steps, y_min_steps):
            scan_poly_width, scan_poly_height = self.text_width_height
            x_max = x_min + scan_poly_width
            y_max = y_min + scan_poly_height
            scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                                  x_min=x_min,
                                                  y_min=y_min,
                                                  x_max=x_max,
                                                  y_max=y_max)
            scan_poly = TypedPolygon(poly=scan_poly,
                                     poly_type='text')
            scan_result = poly_result.PolyResult(poly=scan_poly,
                                                 poly_type='scan_poly',
                                                 num_iterations=num_iterations)
            intersecting_polys = spatial_analysis_functions.get_intersecting_polys(rtree_idx=rtree_idx,
                                                                                   scan_poly=scan_poly,
                                                                                   ignore_polys=[self.city_poly])
            non_starter_polys = [poly for poly in intersecting_polys if
                                 poly.poly_type in unacceptable_scan_overlap_types]
            if len(non_starter_polys) > 0:
                continue

            yield scan_result

            for poly in intersecting_polys:
                result = poly_result.PolyResult(poly=poly,
                                                poly_type='intersecting',
                                                num_iterations=num_iterations)
                yield result

            scan_poly_intersections = ScanPoly(poly=scan_poly,
                                               intersecting_polys=intersecting_polys)
            self.scan_polys_manager.add_scan_poly(scan_poly_intersections)

            num_iterations += 1

    def _determine_nearest_polys(self, scan_polys: list[TypedPolygon], rtree_idx, polygons):
        nearby_poly_search_width = get_config_value(config, 'algorithm.nearby_poly_search_width', int)
        nearby_poly_search_height = get_config_value(config, 'algorithm.nearby_poly_search_height', int)

        num_iterations = 0
        for scan_poly in scan_polys:
            scan_result = poly_result.PolyResult(poly=scan_poly,
                                                 poly_type='finalist_poly',
                                                 num_iterations=num_iterations)
            yield scan_result
            center_coord = scan_poly.poly.centroid.x, scan_poly.poly.centroid.y
            nearby_search_poly = poly_creation.create_poly(poly_type='rectangle',
                                                           center_coord=center_coord,
                                                           poly_width=nearby_poly_search_width,
                                                           poly_height=nearby_poly_search_height)
            nearby_search_result = poly_result.PolyResult(poly=nearby_search_poly,
                                                          poly_type='nearby_search_poly',
                                                          num_iterations=num_iterations)
            yield nearby_search_result
            nearby_search_poly_bounds = nearby_search_poly.bounds
            nearby_poly_idxs = list(rtree_idx.intersection(nearby_search_poly_bounds))
            nearest_polys = [polygons[idx] for idx in nearby_poly_idxs]
            scan_poly.nearest_polys = nearest_polys

            num_iterations += 1

    def find_best_poly(self, rtree_analyzer: RtreeAnalyzer):
        max_text_distance_to_city = get_config_value(config, 'algorithm.maximum_distance_to_city', int)

        scan_area_poly = self._create_scan_area_poly(max_text_distance_to_city=max_text_distance_to_city)
        yield poly_result.PolyResult(poly=scan_area_poly,
                                     poly_type='scan_area',
                                     num_iterations=0)
        x_min_steps, y_min_steps = _create_scan_steps(text_box_dimensions=self.text_box_dimensions,
                                                      scan_area_poly=scan_area_poly)
        for result in self._run_initial_scan(x_min_steps, y_min_steps, rtree_idx=rtree_analyzer.rtree_idx):
            yield result

        finalist_scan_polys = self.scan_polys_manager.get_least_intersections_poly_groups(
            poly_types_to_omit=['scatter', 'text'])

        for result in self._determine_nearest_polys(scan_polys=finalist_scan_polys,
                                                    rtree_idx=rtree_analyzer.rtree_idx,
                                                    polygons=rtree_analyzer.polygons):
            yield result

        scoring.score_scan_polys(city_poly=self.city_poly,
                                 scan_polys=finalist_scan_polys)
        best_scan_poly = finalist_scan_polys[0]
        for scan_poly in finalist_scan_polys[1:]:
            if scan_poly.score > best_scan_poly.score:
                best_scan_poly = scan_poly

        yield poly_result.PolyResult(poly=best_scan_poly,
                                     poly_type='best_poly',
                                     num_iterations=-1)
