from shapely import Point


def get_distance_between_elements(item1, item2):
    if isinstance(item1, tuple):
        item1 = Point(item1)
    if isinstance(item2, tuple):
        item2 = Point(item2)
    distance = item1.distance(item2)
    return distance


def get_intersecting_polys(rtree_idx, polygons, scan_poly, ignore_polys: list) -> list:
    intersection_indices = list(rtree_idx.intersection(scan_poly.bounds))
    intersecting_polygons = [polygons[idx] for idx in intersection_indices]
    intersecting_polygons = [t_poly for t_poly in intersecting_polygons if scan_poly.intersects(t_poly) and
                             t_poly not in ignore_polys]
    return intersecting_polygons
