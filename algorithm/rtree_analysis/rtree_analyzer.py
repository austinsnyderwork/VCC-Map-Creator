import numpy as np
from rtree import index
from shapely.geometry import Polygon

import poly_creation
from . import helper_functions


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

    def _determine_best_poly(self, scan_poly_intersections: dict, city_coord: tuple) -> Polygon:
        scan_poly_intersections = dict(sorted(scan_poly_intersections.items()))
        non_text_intersecting_groups = []
        for num_intersections, poly_groups in scan_poly_intersections.items():
            found_non_text_group = False
            for scan_poly, intersecting_polys in poly_groups:
                non_text_polys = [poly for poly in intersecting_polys if
                                  self.poly_classes[self._generate_poly_key(poly)] == 'text']
                if len(non_text_polys) > 0:
                    found_non_text_group = True
                    non_text_intersecting_groups.append((scan_poly, intersecting_polys))
            if found_non_text_group:
                break

        # If there are no groups without a text box intersection, then proceed as normal with the groups with the lowest
        # number of intersections
        if len(non_text_intersecting_groups) == 0:
            poly_groups = next(iter(scan_poly_intersections.values()))
        else:
            poly_groups = non_text_intersecting_groups

        # At some point we may want to consider the proximity to other polygons, but for now we just pick the polygon
        # closest to the city
        search_polys = list(poly_groups.keys())
        closest_scan_poly = helper_functions.find_closest_poly(search_polys=search_polys,
                                                               center_point=city_coord)
        return closest_scan_poly

    def _get_intersecting_polys(self, scan_poly) -> list[Polygon]:
        intersection_indices = list(self.rtree_idx.intersection(scan_poly.bounds))
        intersecting_polygons = [self.polygons[idx] for idx in intersection_indices]
        intersecting_polygons = [poly for poly in intersecting_polygons if scan_poly.intersects(poly)]
        return intersecting_polygons

    def find_available_poly_around_point(self, scan_poly, search_area_poly, search_steps=100):
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
                yield scan_poly, 'scan_poly'

                intersecting_polys = self._get_intersecting_polys(scan_poly=scan_poly)

                poly_groups_dict[self._generate_poly_key(poly=scan_poly)] = intersecting_polys
                for poly in intersecting_polys:
                    yield poly, 'intersecting'

        best_poly = self._determine_best_poly(scan_poly_intersections=poly_groups_dict,
                                              city_coord=(search_area_poly.centroid.x, search_area_poly.centroid.y))
        yield best_poly, 'best_poly'
