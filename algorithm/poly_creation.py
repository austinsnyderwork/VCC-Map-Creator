import itertools
import logging
import matplotlib.patches as patches
import numpy as np
from shapely.geometry import Polygon

from . import helper_functions


def create_poly(poly_type: str, **kwargs):
    poly_create_functions = {
        'line': _create_line_polygon,
        'scatter': _create_circle_polygon,
        'rectangle': _create_rectangle_polygon
    }
    func = poly_create_functions[poly_type]
    poly = func(**kwargs)
    return poly


def _create_line_polygon(line_width: float, x_data, y_data) -> Polygon:
    line_coord_0 = (x_data[0], y_data[0])
    line_coord_1 = (x_data[1], y_data[1])

    slope = (y_data[1] - y_data[0]) / (x_data[1] - x_data[0])
    perpendicular_slope = -1 / slope

    poly_coords = []
    for coord in [line_coord_0, line_coord_1]:
        new_coord_0 = helper_functions.move_coordinate(coord[0], coord[1], slope=perpendicular_slope,
                                                       distance=line_width / 2)
        new_coord_1 = helper_functions.move_coordinate(coord[0], coord[1], slope=-perpendicular_slope,
                                                       distance=line_width / 2)
        poly_coords.append(new_coord_0)
        poly_coords.append(new_coord_1)

    poly = _create_polygon_from_coords(coords=poly_coords)
    return poly


def _create_circle_polygon(center, radius, num_points=100) -> Polygon:
    angles = np.linspace(0, 2 * np.pi, num_points)
    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    return Polygon(points)


def _create_rectangle_polygon(**kwargs) -> Polygon:
    if 'lon' in kwargs and 'lat' in kwargs and 'width' in kwargs and 'height' in kwargs:
        lon = kwargs['lon']
        lat = kwargs['lat']
        width = kwargs['width']
        height = kwargs['height']
        x_min = lon - width
        x_max = lon + width
        y_min = lat - height
        y_max = lat + height
    else:
        x_min = kwargs['x_min']
        y_min = kwargs['y_min']
        x_max = kwargs['x_max']
        y_max = kwargs['y_max']

    coordinates = [
        (x_min, y_min),  # Bottom-left corner
        (x_max, y_min),  # Bottom-right corner
        (x_max, y_max),  # Top-right corner
        (x_min, y_max),  # Top-left corner
        (x_min, y_min)  # Closing the polygon by returning to the start
    ]

    # Create and return the Polygon
    return Polygon(coordinates)


def _create_polygon_from_coords(**kwargs):
    poly = None
    # This indicates that we were given individual coordinates
    if 'min_x' in kwargs:
        logging.info("Creating polygon from coords.")
        min_x = kwargs['min_x']
        max_x = kwargs['max_x']
        min_y = kwargs['min_y']
        max_y = kwargs['max_y']

        polygon_coords = [
            (min_x, min_y),  # Bottom-left
            (max_x, min_y),  # Bottom-right
            (max_x, max_y),  # Top-right
            (min_x, max_y),  # Top-left
            (min_x, min_y)  # Close the polygon
        ]

        poly = Polygon(polygon_coords)
    else:
        logging.info("Creating polygon from coord permutations.")
        for permutation in itertools.permutations(kwargs['coords']):
            polygon = Polygon(permutation)
            if polygon.is_valid:
                poly = polygon
                break

    if not poly.is_valid:
        raise ValueError("Could not form a valid polygon.")
    else:
        return poly


def resize_rectangle(min_x, min_y, max_x, max_y, factor):
    # Calculate the center of the original rectangle
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # Calculate the original width and height
    original_width = max_x - min_x
    original_height = max_y - min_y

    # Calculate new width and height based on the given factor
    new_width = original_width / factor
    new_height = original_height / factor

    # Calculate new min and max coordinates
    new_min_x = center_x - new_width / 2
    new_max_x = center_x + new_width / 2
    new_min_y = center_y - new_height / 2
    new_max_y = center_y + new_height / 2

    return new_min_x, new_min_y, new_max_x, new_max_y
