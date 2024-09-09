import numpy as np
from rtree import index
from shapely.geometry import Polygon

from algorithm import poly_creation
from . import helper_functions


class RtreeAnalyzer:

    def __init__(self):
        self.rtree_idx = index.Index()

        self.polygons = {}
        self.poly_types = {}
        self.poly_idx = 0

    def _get_intersecting_polys(self, scan_poly) -> list[Polygon]:
        intersection_indices = list(self.rtree_idx.intersection(scan_poly.bounds))
        intersecting_polygons = [self.polygons[idx] for idx in intersection_indices]
        intersecting_polygons = [poly for poly in intersecting_polygons if scan_poly.intersects(poly)]
        return intersecting_polygons

    @staticmethod
    def _generate_poly_key(poly: Polygon):
        return (poly,)

    def add_poly(self, poly: Polygon, poly_type: str):
        self.rtree_idx.insert(self.poly_idx, poly.bounds, obj=poly)
        poly_key = self._generate_poly_key(poly=poly)
        self.polygons[self.poly_idx] = poly
        self.poly_types[poly_key] = poly_type
        self.poly_idx += 1

    def _determine_best_poly(self, scan_poly_intersections: dict, city_coord: tuple) -> Polygon:
        scan_poly_intersections = dict(sorted(scan_poly_intersections.items()))
        non_text_intersecting_groups = []
        for num_intersections, poly_groups in scan_poly_intersections.items():
            found_non_text_group = False
            for scan_poly, intersecting_polys in poly_groups:
                non_text_polys = [poly for poly in intersecting_polys if
                                  self.poly_types[self._generate_poly_key(poly)] == 'text']
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

    def find_available_poly_around_point(self, search_area_bounds: dict, city_coord, text_width: float,
                                         text_height: float, search_steps=100):
        """
        Create the equally-spaced steps between the start and end of both the width and height of the search area. We
        obviously can't allow the right border of the scan poly to go past the right border of the search area, so
        we limit how far the x_min can go by the x_max of the search area minus the width of the scan poly. Same is true
        for the y-axis with the height.
        """
        search_area_min_x = search_area_bounds['min_x']
        search_area_min_y = search_area_bounds['min_y']
        search_area_max_x = search_area_bounds['max_x']
        search_area_max_y = search_area_bounds['max_y']

        search_area_poly = poly_creation.create_poly(poly_type='rectangle', min_x=search_area_min_x,
                                                     min_y=search_area_min_y, max_x=search_area_max_x,
                                                     max_y=search_area_max_y)
        yield search_area_poly, 'search_area'

        search_poly_x_len = search_area_max_x - search_area_min_x
        search_poly_y_len = search_area_max_y - search_area_min_y

        # Iterating steps through
        maximum_x_min = search_area_max_x - text_width
        min_x_steps = np.linspace(search_area_min_x, maximum_x_min, search_steps)

        maximum_y_min = search_area_max_y - text_height
        min_y_steps = np.linspace(search_area_min_y, maximum_y_min, search_steps)

        scan_poly_intersections = {}

        iteration = 0
        for x_min in min_x_steps:
            for y_min in min_y_steps:
                x_max = x_min + search_poly_x_len
                y_max = y_min + search_poly_y_len
                scan_poly = poly_creation.create_poly(poly_type='rectangle',
                                                      x_min=x_min,
                                                      y_min=y_min,
                                                      x_max=x_max,
                                                      y_max=y_max)
                yield scan_poly, 'scan_poly', iteration

                intersecting_polys = self._get_intersecting_polys(scan_poly=scan_poly)
                for poly in intersecting_polys:
                    yield poly, 'intersecting'

                num_intersections = len(intersecting_polys)
                if num_intersections not in scan_poly_intersections:
                    scan_poly_intersections[num_intersections] = []
                scan_poly_intersections[num_intersections].append((scan_poly, intersecting_polys))

                iteration += 1

        best_poly = self._determine_best_poly(scan_poly_intersections=scan_poly_intersections,
                                              city_coord=city_coord)
        return best_poly
