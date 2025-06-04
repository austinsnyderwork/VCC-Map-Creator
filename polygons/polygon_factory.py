import numpy as np
from shapely.geometry import Polygon, LineString, box

from shared.shared_utils import Coordinate
from . import polygon_utils


class PolygonFactory:

    @staticmethod
    def create_line(coord_0: Coordinate,
                    coord_1: Coordinate,
                    line_width: float
                    ) -> Polygon:
        line = LineString([coord_0, coord_1])
        line = line.buffer(line_width / 2)
        return line

    @staticmethod
    def create_scatter(coord: Coordinate,
                       radius: int = 100,
                       num_points=8
                       ) -> Polygon:
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        points = [(coord.lon + radius * np.cos(angle),
                   coord.lat + radius * np.sin(angle))
                  for angle in angles]
        points.append(points[0])  # Close the polygon ring
        return Polygon(points)

    @staticmethod
    def create_rectangle(x_min,
                         x_max,
                         y_min,
                         y_max) -> Polygon:
        return box(x_min, y_min, x_max, y_max)

