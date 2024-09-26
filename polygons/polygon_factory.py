import itertools
import logging
import numpy as np
from shapely.geometry import Polygon

from polygons import helper_functions
from . import typed_polygon
from things.visualization_elements import visualization_elements
from things import box_geometry


def create_poly(poly_type: typed_polygon.TypedPolygon, **kwargs) -> Polygon:
    poly_create_functions = {
        typed_polygon.LinePolygon: _create_line_polygon,
        typed_polygon.ScatterPolygon: _create_scatter_polygon,
        typed_polygon.ScanPolygon: _create_rectangle_polygon,
        typed_polygon.FinalistPolygon: _create_rectangle_polygon,
        typed_polygon.NearbySearchPolygon: _create_rectangle_polygon,
        typed_polygon.ScanAreaPolygon: _create_rectangle_polygon
    }
    func = poly_create_functions[poly_type]
    try:
        poly = func(**kwargs)
    except TypeError:
        logging.error(f"Error when attempting to create polygon from arguments:\n{kwargs}")
        raise TypeError
    return poly


def _create_line_polygon(line_entity: visualization_elements.Line) -> typed_polygon.LinePolygon:
    x_data = line_entity.algorithm_x_data
    y_data = line_entity.algorithm_y_data

    slope = (y_data[1] - y_data[0]) / (x_data[1] - x_data[0])
    perpendicular_slope = -1 / slope

    poly_coords = []
    for coord in [x_data, y_data]:
        new_coord_0 = helper_functions.move_coordinate(coord[0], coord[1], slope=perpendicular_slope,
                                                       distance=line_entity.algorithm_line_width / 2)
        new_coord_1 = helper_functions.move_coordinate(coord[0], coord[1], slope=-perpendicular_slope,
                                                       distance=line_entity.algorithm_line_width / 2)
        poly_coords.append(new_coord_0)
        poly_coords.append(new_coord_1)

    poly = None
    for permutation in itertools.permutations(poly_coords):
        polygon = Polygon(permutation)
        if polygon.is_valid:
            poly = polygon
            break

    if poly.is_valid:
        line_polygon = typed_polygon.LinePolygon(poly=poly)
        return line_polygon
    else:
        raise ValueError("Could not form a valid line polygon.")


def _create_scatter_polygon(center, radius, num_points=100) -> typed_polygon.ScatterPolygon:
    angles = np.linspace(0, 2 * np.pi, num_points)
    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    poly = Polygon(points)
    scatter_poly = typed_polygon.ScatterPolygon(poly=poly)
    return scatter_poly


def _create_rectangle_polygon(box_geometry_: box_geometry.BoxGeometry) -> Polygon:
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
