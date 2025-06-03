import numpy as np
from shapely.geometry import Polygon

from . import polygon_utils
from shared.shared_utils import Coordinate
from things import box_geometry
from visualization_elements import vis_element_classes


def _has_attributes(obj, attributes: list[str]) -> bool:
    return all(hasattr(obj, attr) for attr in attributes)


def _get_attributes(obj, attributes: list[str]) -> tuple:
    return tuple(getattr(obj, attr) for attr in attributes)


class PolygonFactory:

    @staticmethod
    def create_line(coord_0: Coordinate,
                    coord_1: Coordinate,
                    line_width: float
                    ) -> Polygon:

        # Determine the slope perpendicular to the line
        delta_x = coord_1.lon - coord_0.lon
        delta_y = coord_1.lat - coord_0.lat

        if delta_x == 0:  # vertical line
            perpendicular_slope = 0
        elif delta_y == 0:  # horizontal line
            perpendicular_slope = 1
        else:
            slope = delta_y / delta_x
            perpendicular_slope = -1 / slope

        # Create new points for the corners of the line polygon
        new_coord_00 = polygon_utils.move_coordinate(coord_0.lon,
                                                     coord_0.lat,
                                                     slope=perpendicular_slope,
                                                     distance=line_width / 2)
        new_coord_01 = polygon_utils.move_coordinate(coord_0.lon,
                                                     coord_0.lat,
                                                     slope=-perpendicular_slope,
                                                     distance=line_width / 2)

        new_coord_10 = polygon_utils.move_coordinate(coord_1.lon,
                                                     coord_1.lat,
                                                     slope=perpendicular_slope,
                                                     distance=line_width / 2)
        new_coord_11 = polygon_utils.move_coordinate(coord_1.lon,
                                                     coord_1.lat,
                                                     slope=-perpendicular_slope,
                                                     distance=line_width / 2)
        poly_coords = [new_coord_00, new_coord_10, new_coord_11, new_coord_01]

        return Polygon(poly_coords)

    @staticmethod
    def create_scatter(coord: Coordinate,
                       radius: int = 100,
                       num_points=8
                       ) -> Polygon:
        angles = np.linspace(0, 2 * np.pi, num_points, endpoint=False)
        points = [(coord.lon + radius * np.cos(angle),
                   coord.lat + radius * np.sin(angle))
                  for angle in angles]
        return Polygon(points)

    @staticmethod
    def create_rectangle(coordinate_pack: 'CoordinatePack',
                         vis_element: vis_element_classes.VisualizationElement = None,
                         box: box_geometry.BoxGeometry = None, **kwargs) -> Polygon:
        if vis_element:
            attributes_1 = ['lon', 'lat', 'width', 'height']
            attributes_2 = ['center_coord', 'poly_width']
            attributes_3 = ['x_min', 'y_min', 'x_max', 'y_max']
            if _has_attributes(vis_element, attributes_1):
                lon, lat, width, height = _get_attributes(vis_element, attributes_1)
                x_min = lon - width
                x_max = lon + width
                y_min = lat - height
                y_max = lat + height
            elif _has_attributes(vis_element, attributes_2):
                center_coord, poly_width = _get_attributes(vis_element, attributes_2)
                x_min = center_coord[0] - poly_width
                x_max = center_coord[0] + poly_width
                y_min = center_coord[1] - poly_width
                y_max = center_coord[1] + poly_width
            elif _has_attributes(vis_element, attributes_3):
                x_min, y_min, x_max, y_max = _get_attributes(vis_element, attributes_3)
            else:
                raise ValueError(
                    f"Could not find attributes in this visualization element to create a rectangle polygon")
        elif box:
            x_min = box.x_min
            y_min = box.y_min
            x_max = box.x_max
            y_max = box.y_max
        else:
            raise ValueError("Must explicitly pass either a visualization element or a box geometry.")

        cp = coordinate_pack
        coordinates = [
            (cp.x_min, cp.y_min),  # Bottom-left corner
            (cp.x_max, cp.y_min),  # Bottom-right corner
            (cp.x_max, cp.y_max),  # Top-right corner
            (cp.x_min, cp.y_max),  # Top-left corner
            (cp.x_min, cp.y_min)  # Closing the polygon by returning to the start
        ]

        # Create and return the Polygon
        poly = Polygon(coordinates)
        return poly
