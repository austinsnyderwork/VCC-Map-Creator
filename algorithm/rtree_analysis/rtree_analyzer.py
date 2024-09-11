import logging
import numpy as np
from rtree import index
from shapely.geometry import Point, Polygon

import poly_creation


class RtreeAnalyzer:

    def __init__(self):
        self.rtree_idx = index.Index()

        self.polygons = {}
        self.poly_classes = {}
        self.poly_idx = 0

    @staticmethod
    def _generate_poly_key(poly: Polygon):
        return (poly,)

    def add_poly(self, poly: Polygon, poly_class: str):
        self.rtree_idx.insert(self.poly_idx, poly.bounds, obj=poly)
        poly_key = self._generate_poly_key(poly=poly)
        self.polygons[self.poly_idx] = poly
        self.poly_classes[poly_key] = poly_class
        self.poly_idx += 1

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

    def _calculate_weighted_distance_to_polys(self, poly_point: Point, nearest_polys: list, city_point: Point):
        weighted_distances = []
        for poly in nearest_polys:
            poly_coord = (poly.centroid.x, poly.centroid.y)
            # Skip the city coordinate point
            if Point(poly_coord) == city_point:
                continue
            distance_to_coord = poly.distance(poly_point)
            weighted_distance = distance_to_coord ** 3
            weighted_distances.append(weighted_distance)
        weighted_score = sum(weighted_distances) / len(weighted_distances)
        city_distance = poly_point.distance(city_point)
        return weighted_score * (1 / (city_distance ** 8))

    def _determine_best_poly(self, scan_poly_num_intersections: dict, city_coord: tuple,
                             steps_to_show_poly_finalist: int):
        logging.info("Filtering text and scatter intersections.")
        scan_poly_num_intersections = dict(sorted(scan_poly_num_intersections.items()))
        filtered_poly_groups = {}
        for num_intersections, poly_groups in scan_poly_num_intersections.items():
            found_non_text_scatter_group = False
            for scan_poly, intersecting_polys in poly_groups:
                if not self._is_non_text_scatter_intersecting(intersecting_polys=intersecting_polys):
                    continue

                found_non_text_scatter_group = True
                scan_poly_key = self._generate_poly_key(scan_poly)
                filtered_poly_groups[scan_poly_key] = intersecting_polys

            if found_non_text_scatter_group:
                break

        # If there are no groups without a text box and scatter intersection, then proceed as normal with the groups
        # with the least number of intersections
        if len(filtered_poly_groups) == 0:
            poly_groups = {}
            temp_poly_group = next(iter(scan_poly_num_intersections.values()))
            for scan_poly, intersecting_polys in temp_poly_group:
                poly_groups[self._generate_poly_key(scan_poly)] = intersecting_polys
        else:
            poly_groups = filtered_poly_groups
        logging.info("Filtered text and scatter intersections.")

        logging.info("Filtering poly candidates on distance.")
        poly_distances = {}
        for scan_poly_key, poly_intersections in poly_groups.items():
            scan_poly = scan_poly_key[0]
            distance_to_city = scan_poly.distance(Point(city_coord))
            if distance_to_city not in poly_distances:
                poly_distances[distance_to_city] = []
            poly_distances[distance_to_city].append(scan_poly)
        mean_distance = sum(list(poly_distances.keys())) / len(list(poly_distances.keys()))

        accepted_scan_polys = []
        for poly_distance, polys in poly_distances.items():
            if poly_distance <= mean_distance:
                accepted_scan_polys.extend(polys)

        poly_groups_new = {}
        for scan_poly in accepted_scan_polys:
            poly_key = self._generate_poly_key(scan_poly)
            poly_groups_new[poly_key] = poly_groups[poly_key]
        logging.info("Filtered poly candidates on distance.")

        logging.info("Calculating weighted distances for poly finalists.")
        iterations = 0
        weighted_distances_by_poly = {}
        for scan_poly_key, intersecting_polys in poly_groups_new.items():
            scan_poly = scan_poly_key[0]
            if iterations % steps_to_show_poly_finalist == 0:
                yield scan_poly, 'poly_finalist'
            scan_poly_point = Point((scan_poly.centroid.x, scan_poly.centroid.y))
            nearest_ids = list(self.rtree_idx.nearest(scan_poly_point.bounds, num_results=15))
            text_scatter_polys = [self.polygons[nearest_id] for nearest_id in nearest_ids
                                  if self._get_poly_class(nearest_id) in ('text', 'scatter')]
            # Higher score is better
            weighted_distance = self._calculate_weighted_distance_to_polys(poly_point=scan_poly_point,
                                                                           nearest_polys=text_scatter_polys,
                                                                           city_point=Point(city_coord))
            if weighted_distance not in weighted_distances_by_poly:
                weighted_distances_by_poly[weighted_distance] = []
            weighted_distances_by_poly[weighted_distance].append(scan_poly)
            iterations += 1
        logging.info("Calculated weighted distances for poly finalists.")

        highest_weight = max(list(weighted_distances_by_poly.keys()))
        best_poly = weighted_distances_by_poly[highest_weight][0]
        yield best_poly, 'best_poly'

    def _get_intersecting_polys(self, scan_poly) -> list[Polygon]:
        intersection_indices = list(self.rtree_idx.intersection(scan_poly.bounds))
        intersecting_polygons = [self.polygons[idx] for idx in intersection_indices]
        intersecting_polygons = [poly for poly in intersecting_polygons if scan_poly.intersects(poly)]
        return intersecting_polygons

    def find_available_poly_around_point(self, scan_poly, search_area_poly, steps_to_show_scan_poly: int,
                                         steps_to_show_poly_finalist: int, search_steps=100):
        """
        Create the equally-spaced steps between the start and end of both the width and height of the search area. We
        obviously can't allow the right border of the scan poly to go past the right border of the search area, so
        we limit how far the x_min can go by the x_max of the search area minus the width of the scan poly. Same is true
        for the y-axis with the height.
        """

        search_area_x_min, search_area_y_min, search_area_x_max, search_area_y_max = search_area_poly.bounds

        search_poly_x_min, search_poly_y_min, search_poly_x_max, search_poly_y_max = scan_poly.bounds
        search_poly_x_len = search_poly_x_max - search_poly_x_min
        search_poly_y_len = search_poly_y_max - search_poly_y_min

        # Iterating steps through
        maximum_x_min = search_area_x_max - search_poly_x_len
        x_min_steps = np.linspace(search_area_x_min, maximum_x_min, search_steps)

        maximum_y_min = search_area_y_max - search_poly_y_len
        y_min_steps = np.linspace(search_area_y_min, maximum_y_min, search_steps)

        num_iterations = 0
        poly_groups_dict = {}
        for x_min in x_min_steps:
            for y_min in y_min_steps:
                x_max = x_min + search_poly_x_len
                y_max = y_min + search_poly_y_len
                scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                                      x_min=x_min,
                                                      y_min=y_min,
                                                      x_max=x_max,
                                                      y_max=y_max)
                if num_iterations % steps_to_show_scan_poly == 0:
                    yield scan_poly, 'scan_poly'

                intersecting_polys = self._get_intersecting_polys(scan_poly=scan_poly)

                num_intersections = len(intersecting_polys)
                if num_intersections not in poly_groups_dict:
                    poly_groups_dict[num_intersections] = []
                poly_groups_dict[num_intersections].append((scan_poly, intersecting_polys))
                for poly in intersecting_polys:
                    if num_iterations % steps_to_show_scan_poly == 0:
                        yield poly, 'intersecting'

                num_iterations += 1

        for poly, poly_type in self._determine_best_poly(
                scan_poly_num_intersections=poly_groups_dict,
                city_coord=(search_area_poly.centroid.x, search_area_poly.centroid.y),
                steps_to_show_poly_finalist=steps_to_show_poly_finalist):
            yield poly, poly_type
