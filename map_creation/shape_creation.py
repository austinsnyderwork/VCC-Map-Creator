import matplotlib.pyplot as plt
import numpy as np

import helper_functions

def create_line_polygon(line: plt.Line2D) -> Polygon:
    line_width = line.get_linewidth()
    x_data = line.get_xdata()
    y_data = line.get_ydata()

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

    poly = create_polygon_from_coords(coords=poly_coords)
    return poly


def create_circle_polygon(center, radius, num_points=100) -> Polygon:
    angles = np.linspace(0, 2 * np.pi, num_points)
    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    return Polygon(points)


def create_rectangle_polygon(x_coords, y_coords) -> Polygon:
    coordinates = [
        (x_coords[0], y_coords[0]),  # Bottom-left corner
        (x_coords[1], y_coords[0]),  # Bottom-right corner
        (x_coords[1], y_coords[1]),  # Top-right corner
        (x_coords[0], y_coords[1]),  # Top-left corner
        (x_coords[0], y_coords[0])  # Closing the polygon by returning to the start
    ]

    # Create and return the Polygon
    return Polygon(coordinates)
