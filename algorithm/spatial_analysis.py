from shapely import Point

from .poly_management import TypedPolygon


def get_distance_between_elements(item1, item2):
    if isinstance(item1, tuple):
        item1 = Point(item1)
    if isinstance(item2, tuple):
        item2 = Point(item2)
    distance = item1.distance(item2)
    return distance


def get_intersecting_polys(rtree_idx, polygons, scan_poly: TypedPolygon, ignore_polys: list[TypedPolygon]) -> list:
    intersection_indices = list(rtree_idx.intersection(scan_poly.bounds))
    intersecting_polygons = [polygons[idx] for idx in intersection_indices]
    intersecting_polygons = [poly for poly in intersecting_polygons if scan_poly.intersects(poly) and
                             poly not in ignore_polys]
    return intersecting_polygons


