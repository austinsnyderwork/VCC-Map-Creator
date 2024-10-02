import itertools
import logging
import numpy as np
from shapely.geometry import Polygon
from typing import Type

from polygons import helper_functions
from things import box_geometry
from things.visualization_elements import visualization_elements


def _has_attributes(obj, attributes: list[str]) -> bool:
    return all(hasattr(obj, attr) for attr in attributes)


def _get_attributes(obj, attributes: list[str]) -> tuple:
    return tuple(getattr(obj, attr) for attr in attributes)


class PolygonFactory:

    def __init__(self, radius_per_scatter_size: int, units_per_line_width: int):
        self.radius_per_scatter_size = radius_per_scatter_size
        self.unit_per_line_width = units_per_line_width

        self.poly_create_functions_by_type = {
            visualization_elements.Line: self._create_line_polygon,
            visualization_elements.CityScatter: self._create_scatter_polygon,
            visualization_elements.CityTextBox: self._create_rectangle_polygon,
            visualization_elements.TextBoxFinalist: self._create_rectangle_polygon,
            visualization_elements.TextBoxNearbySearchArea: self._create_rectangle_polygon,
            visualization_elements.TextBoxScanArea: self._create_rectangle_polygon
        }

    def create_poly(self, vis_element: visualization_elements.VisualizationElement = None,
                    vis_element_type: Type[visualization_elements.VisualizationElement] = None,
                    **kwargs) -> Polygon:
        if vis_element:
            vis_element_type = type(vis_element)
        func = self.poly_create_functions_by_type[vis_element_type]
        poly = func(vis_element,
                    **kwargs)
        return poly

    def _create_line_polygon(self, line_element: visualization_elements.Line, **kwargs) -> Polygon:
        x_data = line_element.x_data
        y_data = line_element.y_data

        slope = (y_data[1] - y_data[0]) / (x_data[1] - x_data[0])
        perpendicular_slope = -1 / slope

        poly_coords = []
        for coord in zip(x_data, y_data):
            new_coord_0 = helper_functions.move_coordinate(coord[0], coord[1], slope=perpendicular_slope,
                                                           distance=line_element.map_linewidth / 2)
            new_coord_1 = helper_functions.move_coordinate(coord[0], coord[1], slope=-perpendicular_slope,
                                                           distance=line_element.map_linewidth / 2)
            poly_coords.append(new_coord_0)
            poly_coords.append(new_coord_1)

        for permutation in itertools.permutations(poly_coords):
            polygon = Polygon(permutation)
            if polygon.is_valid:
                return polygon

        raise ValueError("Could not form a valid line polygon.")

    def _create_scatter_polygon(self, vis_element: visualization_elements.VisualizationElement,
                                num_points=8, **kwargs) -> Polygon:
        angles = np.linspace(0, 2 * np.pi, num_points)
        radius = vis_element.map_size * self.radius_per_scatter_size
        points = [(vis_element.algorithm_coord[0] + radius * np.cos(angle),
                   vis_element.algorithm_coord[1] + radius * np.sin(angle)) for
                  angle in angles]
        poly = Polygon(points)
        return poly

    @staticmethod
    def _create_rectangle_polygon(vis_element: visualization_elements.VisualizationElement = None,
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
                raise ValueError(f"Could not find attributes in this visualization element to create a rectangle polygon")
        elif box:
            x_min = box.x_min
            y_min = box.y_min
            x_max = box.x_max
            y_max = box.y_max

        coordinates = [
            (x_min, y_min),  # Bottom-left corner
            (x_max, y_min),  # Bottom-right corner
            (x_max, y_max),  # Top-right corner
            (x_min, y_max),  # Top-left corner
            (x_min, y_min)  # Closing the polygon by returning to the start
        ]

        # Create and return the Polygon
        poly = Polygon(coordinates)
        return poly
