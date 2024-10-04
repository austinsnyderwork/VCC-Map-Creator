import math

from . import rtree_analyzer
from polygons import polygon_factory
from things import box_geometry
from things.visualization_elements import vis_element_classes


def get_intersecting_vis_elements(rtree_analyzer_: rtree_analyzer.RtreeAnalyzer, city_text_box: vis_element_classes.CityTextBox,
                                  ignore_elements: list[vis_element_classes.VisualizationElement] = None) -> list:
    intersection_indices = list(rtree_analyzer_.rtree_idx.intersection(city_text_box.algorithm_poly.bounds))
    intersecting_vis_elements = [rtree_analyzer_.visualization_elements[idx] for idx in intersection_indices]
    filtered_vis_elements = []
    for vis_element in intersecting_vis_elements:
        if vis_element in ignore_elements:
            continue
        filtered_vis_elements.append(vis_element)

    filtered_vis_elements = [vis_element for vis_element in filtered_vis_elements if city_text_box.algorithm_poly.intersects(vis_element.poly)]
    return filtered_vis_elements


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


def move_text_box_to_bottom_left_city_box_corner(text_box: box_geometry.BoxGeometry,
                                                 city_box: box_geometry.BoxGeometry):
    # Text box to the right of city box
    if text_box.x_max > city_box.x_max:
        x_distance = text_box.x_max - city_box.x_min
        text_box.move_box('left', x_distance)
    # Text box to the left of city box
    else:
        x_distance = city_box.x_min - text_box.x_max
        text_box.move_box('right', x_distance)

    # Text box above city box
    if text_box.y_max > city_box.y_max:
        y_distance = text_box.y_max - city_box.y_min
        text_box.move_box('down', y_distance)
    else:
        # Text box below city box
        y_distance = city_box.y_min - text_box.y_max
        text_box.move_box('up', y_distance)


def verify_poly_validity(poly, name):
    if not poly.is_valid:
        raise ValueError(f"{name} poly was invalid on creation.")


def reduce_poly_width(polygon_factory_: polygon_factory.PolygonFactory, poly, width_adjustment: float):
    x_min, y_min, x_max, y_max = poly.bounds
    poly_width = x_max - x_min
    width_adjust_percent = width_adjustment / 100.0
    width_change = poly_width * width_adjust_percent
    x_min = x_min + (width_change / 2)
    x_max = x_max - (width_change / 2)
    poly = polygon_factory_.create_poly(poly_type='rectangle',
                                        x_min=x_min,
                                        y_min=y_min,
                                        x_max=x_max,
                                        y_max=y_max)
    return poly

