import math
from enum import Enum

from shapely import Polygon

from .polygon_factory import PolygonFactory


class CoordinatePack:

    def __init__(self,
                 x_min: float,
                 x_max: float,
                 y_min: float,
                 y_max: float):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max


def verify_poly(poly, name):
    if not poly.is_valid:
        raise ValueError(f"{name} poly was invalid on creation.")


class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


def get_polygon_bounds(poly):
    x_min, y_min, x_max, y_max = poly.bounds
    return {
        'x_min': x_min,
        'y_min': y_min,
        'x_max': x_max,
        'y_max': y_max
    }


def move_poly(direction: Direction, distance: float, cpack: CoordinatePack = None):
    if direction == Direction.UP:
        cpack.y_min += distance
        cpack.y_max += distance
    elif direction == Direction.DOWN:
        cpack.y_min -= distance
        cpack.y_max -= distance
    elif direction == Direction.LEFT:
        cpack.x_min -= distance
        cpack.x_max -= distance
    elif direction == Direction.RIGHT:
        cpack.y_min += distance
        cpack.y_max += distance


def move_coordinate(x, y, slope, distance) -> tuple:
    angle = math.atan(slope)  # arctan gives the angle from the slope

    # Calculate the change in x and y using the angle and distance
    delta_x = distance * math.cos(angle)  # Adjacent side of the right triangle
    delta_y = distance * math.sin(angle)  # Opposite side of the right triangle

    # Calculate new coordinates
    new_x = x + delta_x
    new_y = y + delta_y

    return new_x, new_y


def thin_rectangle(rectangle: Polygon, width_adjustment: float):
    x_min, y_min, x_max, y_max = rectangle.bounds
    poly_width = x_max - x_min
    width_adjust_percent = width_adjustment / 100.0
    width_change = poly_width * width_adjust_percent
    x_min = x_min + (width_change / 2)
    x_max = x_max - (width_change / 2)
    coordinate_pack = CoordinatePack(
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max
    )
    poly = PolygonFactory.create_rectangle(coordinate_pack=coordinate_pack)
    return poly
