import numpy as np
from shapely.geometry import Polygon


class RtreeAnalyzer:

    def __init__(self, rtree_idx):
        self.rtree_idx = rtree_idx

        self.polygons = {}
        self.poly_idx = 0

    def get_intersecting_polygons(self, search_polygon, rtree_idx) -> list[Polygon]:
        intersection_indices = list(rtree_idx.intersection(search_polygon.bounds))
        intersecting_polygons = [self.polygons[idx] for idx in intersection_indices]
        intersecting_polygons = [poly for poly in intersecting_polygons if search_polygon.intersects(poly)]
        return intersecting_polygons

    def add_polygon(self, poly: Polygon):
        self.rtree_idx.insert(self.poly_idx, poly.bounds, obj=poly)
        self.polygons[self.poly_idx] = poly
        self.poly_idx += 1

    def find_available_polygon_around_point(self, search_poly: Polygon, point, search_steps=100):
        search_area_min_x, search_area_min_y, search_area_max_x, search_area_max_y = search_poly.bounds

        search_poly_min_x, search_poly_min_y, search_poly_max_x, search_poly_max_y = search_poly.bounds
        search_poly_x_len = search_poly_max_x - search_poly_min_x
        search_poly_y_len = search_poly_max_y - search_poly_min_y

        least_poly_intersections = 100

        # Iterating steps through
        maximum_x_min = search_area_max_x - search_poly_x_len
        min_x_steps = np.linspace(search_area_min_x, maximum_x_min, search_steps)

        maximum_y_min = search_area_max_y - search_poly_y_len
        min_y_steps = np.linspace(search_area_min_y, maximum_y_min, search_steps)

        idx = 0
        poly_groups_dict = {}
        search_polys = {}

        search_patch = None
        num_steps_total = 0
        for min_x in min_x_steps:
            for min_y in min_y_steps:
                max_x = min_x + search_poly_x_len
                max_y = min_y + search_poly_y_len
                search_poly = create_rectangle_polygon(x_coords=(min_x, max_x),
                                                       y_coords=(min_y, max_y))

                intersecting_polys = get_intersecting_polygons(search_polygon=search_poly,
                                                               rtree_idx=rtree_idx,
                                                               polygons=polygons)
                poly_groups_dict[idx] = intersecting_polys
                search_polys[idx] = search_poly
                idx += 1

                if should_show_algorithm_search_display and num_steps_total % num_steps_to_show_algorithm_poly == 0:
                    search_patch = add_polygon_to_axis(poly=search_poly,
                                                       set_axis=False,
                                                       color='green',
                                                       transparency=1.0)
                    intersect_patches = []
                    for poly in intersecting_polys:
                        intersect_patch = add_polygon_to_axis(poly=poly,
                                                              set_axis=False,
                                                              color='red',
                                                              transparency=1.0)
                        intersect_patches.append(intersect_patch)
                    for intersect_patch in intersect_patches:
                        intersect_patch.remove()

                if search_patch:
                    search_patch.remove()
                    search_patch = None

        if least_poly_intersections == 0:
            closest_poly = find_closest_poly(list(search_polys.values()), search_area_poly.centroid)
            return closest_poly

        best_poly = determine_best_poly_group(intersecting_poly_groups=intersecting_poly_groups,
                                              search_polys=search_polys,
                                              city_point=search_area_poly.centroid)
        return best_poly


