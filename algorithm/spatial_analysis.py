from shapely import Point

from .poly_management import TypedPolygon


def get_distance_between_elements(item1, item2):
    if isinstance(item1, tuple):
        item1 = Point(item1)
    if isinstance(item2, tuple):
        item2 = Point(item2)
    distance = item1.distance(item2)
    return distance


def get_intersecting_polys(rtree_idx, polygons, scan_poly: TypedPolygon, attributes_of_polys_to_ignore: dict = None) -> list:
    intersection_indices = list(rtree_idx.intersection(scan_poly.bounds))
    intersecting_polygons = [polygons[idx] for idx in intersection_indices]
    filtered_polys = []
    for poly in intersecting_polygons:
        should_omit = False
        if attributes_of_polys_to_ignore:
            for omit_key, omit_value in attributes_of_polys_to_ignore.items():
                if hasattr(poly, omit_key):
                    if getattr(poly, omit_key) == omit_value:
                        should_omit = True
        if should_omit:
            continue
        filtered_polys.append(poly)
    intersecting_polygons = [poly for poly in filtered_polys if scan_poly.intersects(poly)]
    return intersecting_polygons


