from shapely.geometry import Polygon, Point


def find_closest_poly(search_polys: list[Polygon], center_coord):
    shortest_distance = 999999999
    best_poly = None
    center_point = Point(center_coord)
    for search_poly in search_polys:
        distance = search_poly.distance(center_point)
        if distance < shortest_distance:
            shortest_distance = distance
            best_poly = search_poly
    return best_poly
