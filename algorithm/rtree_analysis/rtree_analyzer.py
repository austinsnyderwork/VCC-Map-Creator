import logging
import numpy as np
from rtree import index
from shapely.geometry import Point, Polygon

from algorithm.poly_management import PolyGroup, TypedPolygon, PolyGroupsManager
import poly_creation
from .. import poly_management, poly_result


class RtreeAnalyzer:

    def __init__(self):
        self.rtree_idx = index.Index()

        self.polygons = {}
        self.poly_classes = {}
        self.poly_idx = 0

    @staticmethod
    def _generate_poly_key(poly: TypedPolygon):
        return (poly,)

    def add_poly(self, poly: TypedPolygon, poly_class: str):
        self.rtree_idx.insert(self.poly_idx, poly.bounds, obj=poly)
        poly_key = self._generate_poly_key(poly=poly)
        self.polygons[self.poly_idx] = poly
        self.poly_classes[poly_key] = poly_class
        self.poly_idx += 1

    def _scan_poly_outside_of_search_area(self, scan_poly, search_area_poly):
        extruding_scan_poly = scan_poly.difference(search_area_poly)

        return not extruding_scan_poly.is_empty

    def _is_non_text_scatter_intersecting(self, intersecting_polys):
        non_text_polys = [poly for poly in intersecting_polys
                          if self.poly_classes[self._generate_poly_key(poly)] == 'text']
        non_scatter_polys = [poly for poly in intersecting_polys
                             if self.poly_classes[self._generate_poly_key(poly)] == 'scatter']
        return True if len(non_text_polys) == 0 and len(non_scatter_polys) == 0 else False

    def _calculate_weighted_distance_to_polys(self, scan_poly: TypedPolygon, nearest_polys: list):
        weighted_distances = []
        for near_poly in nearest_polys:
            distance_to_coord = scan_poly.distance(near_poly)
            weighted_distance = distance_to_coord ** 3
            weighted_distances.append(weighted_distance)
        logging.info(f"Weighted distances: {weighted_distances}")
        # Higher score means more suitable (farther away from other elements)
        weighted_score = sum(weighted_distances) / len(weighted_distances)
        return weighted_score

    def _determine_nearby_polys(self, poly_groups_manager: PolyGroupsManager, city_coord: tuple,
                                 nearby_poly_search_width: int, nearby_poly_search_height: int):
        logging.info("Filtering text and scatter intersections.")
        least_intersecting_poly_groups = (
            poly_groups_manager.get_least_intersections_poly_groups(poly_types_to_omit=['text', 'scatter']))
        logging.info("Filtered text and scatter intersections.")

        logging.info("Calculating weighted distances for poly finalists.")
        iterations = 0
        poly_distance_scores = []
        city_distance_scores = []
        for poly_group in least_intersecting_poly_groups:
            center_coord = poly_group.poly.centroid.x, poly_group.poly.centroid.y
            nearby_search_poly = poly_creation.create_poly(poly_type='rectangle',
                                                           center_coord=center_coord,
                                                           poly_width=nearby_poly_search_width,
                                                           poly_height=nearby_poly_search_height)
            nearby_search_poly_bounds = nearby_search_poly.bounds
            nearby_poly_idxs = list(self.rtree_idx.intersection(nearby_search_poly_bounds))
            nearest_polys = [self.polygons[idx] for idx in nearby_poly_idxs]
            poly_group.nearest_polys = nearest_polys
        return poly_groups_manager
            # Higher score is better
            distance_score = self._calculate_weighted_distance_to_polys(scan_poly=poly_group.poly,
                                                                        nearest_polys=nearest_polys)
            poly_distance_scores.append(distance_score)
            city_distance = Point(center_coord).distance(Point(city_coord))
            city_distance_scores.append(city_distance)
            logging.info(f"Other polys distance score: {distance_score} | City distance score: {city_distance}")
            finalist_result = poly_result.PolyResult(poly=poly_group.poly,
                                                     poly_type='poly_finalist',
                                                     num_iterations=iterations)
            nearby_search_result = poly_result.PolyResult(poly=nearby_search_poly,
                                                          poly_type='nearby_search',
                                                          num_iterations=iterations)
            yield finalist_result
            yield nearby_search_result
            iterations += 1

        norm_city_distance_scores = []
        mean_poly_distances = np.mean(poly_distance_scores)
        for city_distance_score in city_distance_scores:
            norm_score = city_distance_score / (city_distance_score + mean_poly_distances)
            norm_city_distance_scores.append(norm_score)
        logging.info("Calculated weighted distances for poly finalists.")

        highest_score = max(list(weighted_distances_by_poly.keys()))
        logging.info(f"Highest weight: {highest_score}")
        best_poly = weighted_distances_by_poly[highest_score][0]
        result = poly_result.PolyResult(poly=best_poly,
                                        poly_type='best_poly',
                                        num_iterations=iterations)
        yield result

    def _get_intersecting_polys(self, scan_poly: TypedPolygon, ignore_polys: list[TypedPolygon]) -> list[TypedPolygon]:
        intersection_indices = list(self.rtree_idx.intersection(scan_poly.bounds))
        intersecting_polygons = [self.polygons[idx] for idx in intersection_indices]
        intersecting_polygons = [t_poly for t_poly in intersecting_polygons if scan_poly.intersects(t_poly) and
                                 t_poly not in ignore_polys]
        return intersecting_polygons

    def find_best_poly_around_point(self, scan_poly: TypedPolygon, search_area_poly,
                                    search_steps: int, nearby_poly_search_width: int,
                                    nearby_poly_search_height: int, point_poly: Polygon) -> poly_result.PolyResult:
        """
        Create the equally-spaced steps between the start and end of both the width and height of the search area. We
        obviously can't allow the right border of the scan poly to go past the right border of the search area, so
        we limit how far the x_min can go by the x_max of the search area minus the width of the scan poly. Same is true
        for the y-axis with the height.
        """

        logging.info("\tFinished scan for best poly.")

        logging.info("Determining best poly.")
        determine_iterations = 0
        for result in self._determine_best_finalist(
                poly_groups_manager=poly_groups_manager,
                city_coord=(search_area_poly.centroid.x, search_area_poly.centroid.y),
                nearby_poly_search_width=nearby_poly_search_width,
                nearby_poly_search_height=nearby_poly_search_height):
            yield result
            determine_iterations += 1
        logging.info("\tBest poly determined.")
