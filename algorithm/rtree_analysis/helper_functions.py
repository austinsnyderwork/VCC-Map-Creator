

def find_closest_poly(search_polys, center_point):
    shortest_distance = 999999999
    best_poly = None
    for search_poly in search_polys:
        distance = center_point.centroid.distance(search_poly)
        if distance < shortest_distance:
            shortest_distance = distance
            best_poly = search_poly
    return best_poly
