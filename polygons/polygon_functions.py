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
    # Ensure we have exactly two points
    if len(x_data) != 2 or len(y_data) != 2:
        raise ValueError("x_data and y_data must contain exactly two points.")

    # Extract the coordinates
    x1, y1 = x_data[0], y_data[0]
    x2, y2 = x_data[1], y_data[1]

    # Calculate the length of the line
    length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # Calculate the reduction length
    reduction_length = length * (100 - line_length_reduction_percent) / 100

    # Calculate the new length
    new_length = length - reduction_length

    # Calculate the direction vector
    dx = x2 - x1
    dy = y2 - y1

    # Normalize the direction vector
    norm = math.sqrt(dx ** 2 + dy ** 2)
    dx /= norm
    dy /= norm

    # Calculate the new endpoints
    new_x1 = x1 + dx * (new_length / 2)
    new_y1 = y1 + dy * (new_length / 2)
    new_x2 = x2 - dx * (new_length / 2)
    new_y2 = y2 - dy * (new_length / 2)

    return [new_x1, new_x2], [new_y1, new_y2]

