from shapely import Point
from shapely.geometry import Polygon, LineString, box

from shared.shared_utils import Coordinate


class PolygonFactory:

    @staticmethod
    def create_line(coord_0: Coordinate,
                    coord_1: Coordinate,
                    width: float
                    ) -> Polygon:
        line = LineString([coord_0.lon_lat, coord_1.lon_lat])
        line = line.buffer(width / 2)
        return line

    @staticmethod
    def create_scatter(coord: Coordinate,
                       radius: float
                       ) -> Polygon:
        return Point(coord.lon, coord.lat).buffer(radius)

    @staticmethod
    def create_rectangle(x_min,
                         y_min,
                         x_max,
                         y_max) -> Polygon:
        return box(x_min, y_min, x_max, y_max)
