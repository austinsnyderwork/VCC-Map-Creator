from shapely import Point


def get_distance_between_elements(item1, item2):
    distance = item1.distance(Point(item2))
    return distance
