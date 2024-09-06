

def get_intersecting_polygons(search_polygon, rtree_idx, polygons) -> list[Polygon]:
    intersection_indices = list(rtree_idx.intersection(search_polygon.bounds))
    intersecting_polygons = [polygons[idx] for idx in intersection_indices]
    intersecting_polygons = [poly for poly in intersecting_polygons if search_polygon.intersects(poly)]
    return intersecting_polygons
