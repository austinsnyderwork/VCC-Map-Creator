import logging
import numpy as np
from rtree import index
from shapely.geometry import Point, Polygon

from algorithm.poly_management import PolyGroup, TypedPolygon, PolyGroupsManager
import poly_creation
from .. import poly_management


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
        self.rtree_idx.insert(self.poly_idx, poly.poly.bounds, obj=poly)
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

    def _get_poly_class(self, poly_idx: int):
        poly = self.polygons[poly_idx]
        poly_class = self.poly_classes[self._generate_poly_key(poly=poly)]
        return poly_class

    def _calculate_weighted_distance_to_polys(self, scan_poly: Polygon, nearest_polys: list, city_point: Point):
        weighted_distances = []
        for near_poly in nearest_polys:
            poly_coord = (scan_poly.centroid.x, scan_poly.centroid.y)
            # Skip the city coordinate point
            if Point(poly_coord) == city_point:
                continue
            distance_to_coord = scan_poly.distance(near_poly)
            weighted_distance = distance_to_coord ** 3
            weighted_distances.append(weighted_distance)
        # Higher score means more suitable (farther away from other elements)
        weighted_score = sum(weighted_distances) / len(weighted_distances)

        logging.info(f"Weighted score: {weighted_score}")
        return weighted_score

    def _determine_best_poly(self, poly_groups_manager: PolyGroupsManager, city_coord: tuple,
                             nearby_poly_search_width: int, nearby_poly_search_height: int):
        logging.info("Filtering text and scatter intersections.")
        least_intersecting_poly_groups = (
            poly_groups_manager.get_least_intersections_poly_groups(poly_types_to_omit=['text', 'scatter']))
        logging.info("Filtered text and scatter intersections.")

        logging.info("Calculating weighted distances for poly finalists.")
        iterations = 0
        weighted_distances_by_poly = {}
        for poly_group in least_intersecting_poly_groups:
            center_coord = poly_group.poly.centroid.x, poly_group.poly.centroid.y
            nearby_search_poly = poly_creation.create_poly(poly_type='rectangle',
                                                           poly_width=nearby_poly_search_width,
                                                           poly_height=nearby_poly_search_height,
                                                           center_coord=(
                                                           poly_group.poly.centroid.x, poly_group.poly.centroid.y))
            yield nearby_search_poly, 'nearby_search_poly', iterations
            yield poly_group.poly, 'poly_finalist', iterations
            nearby_search_poly = poly_creation.create_poly(poly_type='rectangle',
                                                           center_coord=center_coord,
                                                           poly_width=nearby_poly_search_width,
                                                           poly_height=nearby_poly_search_height)
            nearby_search_poly_bounds = nearby_search_poly.bounds
            nearby_poly_idxs = list(self.rtree_idx.intersection(nearby_search_poly_bounds))
            nearest_polys = [self.polygons[idx] for idx in nearby_poly_idxs
                             if (self.polygons[idx].centroid.x, self.polygons[idx].centroid.y) not in city_coord]
            # Higher score is better
            distance_score = self._calculate_weighted_distance_to_polys(scan_poly=poly_group.poly,
                                                                        nearest_polys=nearest_polys,
                                                                        city_point=Point(city_coord))
            city_distance = Point(center_coord).distance(Point(city_coord))
            # Again, higher score is better
            city_score = 1 / city_distance
            score = distance_score * city_score
            if distance_score not in weighted_distances_by_poly:
                weighted_distances_by_poly[score] = []

            weighted_distances_by_poly[score].append(poly_group.poly)
            iterations += 1
        logging.info("Calculated weighted distances for poly finalists.")

        highest_score = max(list(weighted_distances_by_poly.keys()))
        logging.info(f"Highest weight: {highest_score}")
        best_poly = weighted_distances_by_poly[highest_score][0]
        yield best_poly, 'best_poly', iterations

    def _get_intersecting_polys(self, scan_poly: TypedPolygon) -> list[TypedPolygon]:
        intersection_indices = list(self.rtree_idx.intersection(scan_poly.bounds))
        intersecting_polygons = [self.polygons[idx] for idx in intersection_indices]
        intersecting_polygons = [t_poly for t_poly in intersecting_polygons if scan_poly.intersects(t_poly.poly)]
        return intersecting_polygons

    def find_best_poly_around_point(self, scan_poly: TypedPolygon, search_area_poly,
                                    search_steps: int, nearby_poly_search_width: int,
                                    nearby_poly_search_height: int) -> (TypedPolygon, str, int):
        """
        Create the equally-spaced steps between the start and end of both the width and height of the search area. We
        obviously can't allow the right border of the scan poly to go past the right border of the search area, so
        we limit how far the x_min can go by the x_max of the search area minus the width of the scan poly. Same is true
        for the y-axis with the height.
        """

        search_area_x_min, search_area_y_min, search_area_x_max, search_area_y_max = search_area_poly.bounds

        scan_poly_x_min, scan_poly_y_min, scan_poly_x_max, scan_poly_y_max = scan_poly.poly.bounds
        scan_poly_x_len = scan_poly_x_max - scan_poly_x_min
        scan_poly_y_len = scan_poly_y_max - scan_poly_y_min

        # Iterating steps through
        maximum_x_min = search_area_x_max - scan_poly_x_len
        x_min_change = (maximum_x_min - search_area_x_min) / search_steps
        x_min_steps = []
        for step in list(range(search_steps + 1)):
            step_distance = x_min_change * step
            x_min_steps.append(search_area_x_min + step_distance)

        maximum_y_min = search_area_y_max - scan_poly_y_len
        y_min_change = (maximum_y_min - search_area_y_min) / search_steps
        y_min_steps = []
        for step in list(range(search_steps + 1)):
            step_distance = y_min_change * step
            y_min_steps.append(search_area_y_min + step_distance)

        poly_groups_manager = PolyGroupsManager()

        num_iterations = 0
        poly_groups_dict = {}
        logging.info("Beginning scan for best poly.")
        for x_min in x_min_steps:
            for y_min in y_min_steps:
                x_max = x_min + scan_poly_x_len
                y_max = y_min + scan_poly_y_len
                scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                                      x_min=x_min,
                                                      y_min=y_min,
                                                      x_max=x_max,
                                                      y_max=y_max)
                scan_poly = TypedPolygon(poly=scan_poly,
                                         poly_type='text')

                intersecting_polys = self._get_intersecting_polys(scan_poly=scan_poly)
                """bad_polys = [poly for poly in intersecting_polys if poly.poly_type in ('text', 'scatter')]
                if len(bad_polys) > 0:
                    continue"""

                yield scan_poly, 'scan_poly', num_iterations
                poly_group = PolyGroup(poly=scan_poly,
                                       intersecting_polys=intersecting_polys)
                poly_groups_manager.add_poly_group(poly_group)

                num_intersections = len(intersecting_polys)
                if num_intersections not in poly_groups_dict:
                    poly_groups_dict[num_intersections] = []

                poly_groups_dict[num_intersections].append(poly_group)
                for poly in intersecting_polys:
                    yield poly, 'intersecting', num_iterations

                num_iterations += 1

        logging.info("\tFinished scan for best poly.")

        logging.info("Determining best poly.")
        determine_iterations = 0
        for poly, poly_type, num_iterations in self._determine_best_poly(
                poly_groups_manager=poly_groups_manager,
                city_coord=(search_area_poly.centroid.x, search_area_poly.centroid.y),
                nearby_poly_search_width=nearby_poly_search_width,
                nearby_poly_search_height=nearby_poly_search_height):
            yield poly, poly_type, determine_iterations
            determine_iterations += 1
        logging.info("\tBest poly determined.")
