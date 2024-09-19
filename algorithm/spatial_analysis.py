import math
from shapely import Point

from .poly_management import TypedPolygon


def get_distance_between_elements(item1, item2):
    if isinstance(item1, tuple):
        item1 = Point(item1)
    if isinstance(item2, tuple):
        item2 = Point(item2)
    distance = item1.distance(item2)
    return distance


def get_intersecting_polys(rtree_idx, polygons, scan_poly: TypedPolygon,
                           attributes_of_polys_to_ignore: dict = None) -> list:
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


def calculate_angle_between_points(x1: float, y1: float, x2: float, y2: float, center_coord: tuple):
    angle1 = math.atan2(y1 - center_coord[1], x1 - center_coord[0])
    angle1 = math.degrees(angle1)
    angle2 = math.atan2(y2 - center_coord[1], x2 - center_coord[0])
    angle2 = math.degrees(angle2)

    return angle1 - angle2


def calculate_angle_from_positive_x_axis(x1: float, y1: float, center_coord: tuple):
    angle = math.atan2(y1 - center_coord[1], x1 - center_coord[0])
    angle = math.degrees(angle)
    if angle < 0:
        angle += 360
    return angle


def can_use_reflex_angle(angle1: float, angle2: float, all_angles: list[float]):
    for angle in all_angles:
        if min(angle1, angle2) < angle < max(angle1, angle2):
            return False
    return True


def find_largest_line_angle(city_coord, line_polys: list[TypedPolygon]):
    angles = {}
    for line_poly in line_polys:
        angle = calculate_angle_from_positive_x_axis(x1=line_poly.centroid.x,
                                                     y1=line_poly.centroid.y,
                                                     center_coord=city_coord)
        angles[angle] = line_poly

    angles = {key: angles[key] for key in sorted(angles.keys())}
    angles_list = list(angles.keys())
    largest_angle = -1
    largest_angle_lines = (None, None)
    for i, (angle, line) in enumerate(angles.items()):
        next_i = i if i < len(angles) else 0
        next_angle = angles_list[next_i]
        if can_use_reflex_angle(angle, next_angle, angles_list):
            result_angle = max(angle, next_angle) - min(angle, next_angle)
        else:
            result_angle =
        next_i = (i + 1) % len(angles_list)
        next_angle = angles_list[next_i]



        angle1 = abs(angle - prev_angle)
        angle2 = abs(angle - next_angle)

        if angle1 > largest_angle:
            largest_angle = angle1
            largest_angle_lines = (line, angles[angle1])
        if angle2 > largest_angle:
            largest_angle = angle2
            largest_angle_lines = (line, angles[angle2])

    return largest_angle, largest_angle_lines
