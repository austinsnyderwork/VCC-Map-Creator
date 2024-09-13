import itertools
import logging
import math
import numpy as np
from shapely.geometry import Polygon

from algorithm import helper_functions


def move_coordinate(x, y, slope, distance) -> tuple:
    angle = math.atan(slope)  # arctan gives the angle from the slope

    # Calculate the change in x and y using the angle and distance
    delta_x = distance * math.cos(angle)  # Adjacent side of the right triangle
    delta_y = distance * math.sin(angle)  # Opposite side of the right triangle

    # Calculate new coordinates
    new_x = x + delta_x
    new_y = y + delta_y

    return new_x, new_y


def create_poly(poly_type: str, **kwargs) -> Polygon:
    poly_create_functions = {
        'line': _create_line_polygon,
        'scatter': _create_circle_polygon,
        'rectangle': _create_rectangle_polygon
    }
    func = poly_create_functions[poly_type]
    try:
        poly = func(**kwargs)
    except TypeError:
        logging.error(f"Error when attempting to create polygon from arguments:\n{kwargs}")
        raise TypeError
    return poly


def _create_line_polygon(line_width: float, x_data, y_data) -> Polygon:
    line_coord_0 = (x_data[0], y_data[0])
    line_coord_1 = (x_data[1], y_data[1])

    slope = (y_data[1] - y_data[0]) / (x_data[1] - x_data[0])
    perpendicular_slope = -1 / slope

    poly_coords = []
    for coord in [line_coord_0, line_coord_1]:
        new_coord_0 = move_coordinate(coord[0], coord[1], slope=perpendicular_slope, distance=line_width / 2)
        new_coord_1 = move_coordinate(coord[0], coord[1], slope=-perpendicular_slope, distance=line_width / 2)
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
    elif 'poly_width' in kwargs and 'poly_height' in kwargs:
        x_min = kwargs['center_coord'][0] - kwargs['poly_width']
        x_max = kwargs['center_coord'][0] + kwargs['poly_width']
        y_min = kwargs['center_coord'][1] - kwargs['poly_height']
        y_max = kwargs['center_coord'][1] + kwargs['poly_height']
        return _create_rectangle_polygon(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max)
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


def _create_polygon_from_coords(**kwargs) -> Polygon:
    poly = None
    for permutation in itertools.permutations(kwargs['coords']):
        polygon = Polygon(permutation)
        if polygon.is_valid:
            poly = polygon
            break

    if not poly.is_valid:
        raise ValueError("Could not form a valid polygon.")
    else:
        return poly
