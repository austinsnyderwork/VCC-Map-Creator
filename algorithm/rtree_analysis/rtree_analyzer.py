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

    def _get_intersecting_polys(self, search_polygon) -> list[Polygon]:
        intersection_indices = list(self.rtree_idx.intersection(search_polygon.bounds))
        intersecting_polygons = [self.polygons[idx] for idx in intersection_indices]
        intersecting_polygons = [poly for poly in intersecting_polygons if search_polygon.intersects(poly)]
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

    def _determine_best_poly(self, scan_poly_intersections: list[tuple], city_point: tuple) -> Polygon:
        non_text_intersecting = []
        for scan_poly, poly_intersections in scan_poly_intersections:
            all_non_text = True
            for poly in poly_intersections:
                poly_key = self._generate_poly_key(poly=poly)
                if self.poly_types[poly_key] == 'text':
                    all_non_text = False
                    break
            if all_non_text:
                non_text_intersecting.append((scan_poly, poly_intersections))

        # Get rid of any poly intersection groups that have a text box in them
        if len(non_text_intersecting) > 0:
            scan_poly_intersections = non_text_intersecting\

        



    def find_available_poly_around_point(self, search_poly_bounds_: dict, search_area_poly: Polygon, search_steps=100):
        """
        Create the equally-spaced steps between the start and end of both the width and height of the search area. We
        obviously can't allow the right border of the scan poly to go past the right border of the search area, so
        we limit how far the x_min can go by the x_max of the search area minus the width of the scan poly. Same is true
        for the y-axis with the height.
        """
        search_area_min_x, search_area_min_y, search_area_max_x, search_area_max_y = search_area_poly.bounds

        search_poly_min_x = search_poly_bounds_['min_x']
        search_poly_min_y = search_poly_bounds_['min_y']
        search_poly_max_x = search_poly_bounds_['max_x']
        search_poly_max_y = search_poly_bounds_['max_y']

        search_poly_x_len = search_poly_max_x - search_poly_min_x
        search_poly_y_len = search_poly_max_y - search_poly_min_y

        least_poly_intersections = 100

        # Iterating steps through
        maximum_x_min = search_area_max_x - search_poly_x_len
        min_x_steps = np.linspace(search_area_min_x, maximum_x_min, search_steps)

        maximum_y_min = search_area_max_y - search_poly_y_len
        min_y_steps = np.linspace(search_area_min_y, maximum_y_min, search_steps)

        scan_poly_intersections = [tuple]

        for x_min in min_x_steps:
            for y_min in min_y_steps:
                x_max = x_min + search_poly_x_len
                y_max = y_min + search_poly_y_len
                search_poly = poly_creation.create_poly(poly_type='rectangle',
                                                        x_min=x_min,
                                                        y_min=y_min,
                                                        x_max=x_max,
                                                        y_max=y_max)

                intersecting_polys = self._get_intersecting_polys(search_polygon=search_poly)
                if len(intersecting_polys) < least_poly_intersections:
                    least_poly_intersections = len(intersecting_polys)
                scan_poly_intersections.append((search_poly, intersecting_polys))

        # If there are poly intersection groups without any intersections, then our best poly is the one that is closest
        # to the city point.
        if least_poly_intersections == 0:
            no_intersections_polys = [tup for tup in scan_poly_intersections if len(tup[1]) == 0]
            search_polys = [_[0] for _ in no_intersections_polys]
            closest_poly = helper_functions.find_closest_poly(search_polys, search_area_poly.centroid)
            return closest_poly

        best_poly = self._determine_best_poly(scan_poly_intersections=scan_poly_intersections,
                                              city_point=search_area_poly.centroid)
        return best_poly
