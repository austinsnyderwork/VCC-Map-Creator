import math


def move_coordinate(x, y, slope, distance) -> tuple:
    angle = math.atan(slope)  # arctan gives the angle from the slope

    # Calculate the change in x and y using the angle and distance
    delta_x = distance * math.cos(angle)  # Adjacent side of the right triangle
    delta_y = distance * math.sin(angle)  # Opposite side of the right triangle

    # Calculate new coordinates
    new_x = x + delta_x
    new_y = y + delta_y

    return new_x, new_y


def move_poly(direction: str, amount: float, dimensions: dict = None):
    if direction == 'up':
        dimensions['y_min'] += amount
        dimensions['y_max'] += amount
    elif direction == 'down':
        dimensions['y_min'] -= amount
        dimensions['y_max'] -= amount
    elif direction == 'right':
        dimensions['x_min'] += amount
        dimensions['x_max'] += amount
    elif direction == 'left':
        dimensions['x_min'] -= amount
        dimensions['x_max'] -= amount


def get_poly_bounds(poly):
    x_min, y_min, x_max, y_max = poly.bounds
    return {
        'x_min': x_min,
        'y_min': y_min,
        'x_max': x_max,
        'y_max': y_max
    }


def _mult_coord(num, coord):
    return coord[0] * num, coord[1] * num


def _add_coords(coord1, coord2):
    return coord1[0] + coord2[0], coord1[1] + coord2[1]


def shorten_line(x_data, y_data, line_length_reduction_percent=15.0):

    coord_1 = x_data[0], y_data[0]
    coord_2 = x_data[1], y_data[1]
    new_coord_1 = _add_coords(_mult_coord(1 - line_length_reduction_percent, coord_1), _mult_coord(line_length_reduction_percent, coord_2))
    new_coord_2 = _add_coords(_mult_coord(line_length_reduction_percent, coord_1), _mult_coord(1 - line_length_reduction_percent, coord_2))

    x_data = new_coord_1[0], new_coord_2[0]
    y_data = new_coord_1[1], new_coord_2[1]
    return x_data, y_data

