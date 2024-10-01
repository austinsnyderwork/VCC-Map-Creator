import math
from shapely import Point

from things.visualization_elements import visualization_elements
from polygons import typed_polygon


def get_distance_between_elements(item1, item2):
    if isinstance(item1, tuple):
        item1 = Point(item1)
    if isinstance(item2, tuple):
        item2 = Point(item2)
    distance = item1.distance(item2)
    return distance


def get_intersecting_polygons(rtree_idx, polygons, scan_element: visualization_elements.TextBoxScan = None,
                              scan_poly: typed_polygon.ScanPolygon = None, attributes_of_polys_to_ignore: dict = None) \
        -> list:
    if scan_element:
        intersection_indices = list(rtree_idx.intersection(scan_element.bounds))
    else:
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


def reduce_line_length(x_data, y_data, line_reduction_units) -> tuple[tuple, tuple]:
    x1 = x_data[0]
    x2 = x_data[1]
    y1 = y_data[0]
    y2 = y_data[1]
    # Step 1: Calculate the direction vector
    direction_vector = (x2 - x1, y2 - y1)

    # Step 2: Calculate the magnitude of the vector
    magnitude = math.sqrt(direction_vector[0] ** 2 + direction_vector[1] ** 2)

    # Step 3: Normalize the direction vector
    unit_vector = (direction_vector[0] / magnitude, direction_vector[1] / magnitude)

    # Step 4: Move the first point 2 units toward the second point
    new_x1 = x1 + line_reduction_units * unit_vector[0]
    new_y1 = y1 + line_reduction_units * unit_vector[1]

    new_x2 = x2 - line_reduction_units * unit_vector[0]
    new_y2 = y2 - line_reduction_units * unit_vector[1]

    return (new_x1, new_x2), (new_y1, new_y2)

