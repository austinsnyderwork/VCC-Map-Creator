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
