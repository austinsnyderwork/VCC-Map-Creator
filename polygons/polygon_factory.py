import itertools
import logging
import numpy as np
from shapely.geometry import Polygon
from typing import Type

from polygons import helper_functions
from . import typed_polygon
from things.visualization_elements import visualization_elements


class PolygonFactory:

    def __init__(self):
        self.vis_element_to_poly_type_map = {
            visualization_elements.Line: typed_polygon.LinePolygon,
            visualization_elements.CityScatter: typed_polygon.ScatterPolygon,
            visualization_elements.TextBoxScan: typed_polygon.ScanPolygon,
            visualization_elements.TextBoxFinalist: typed_polygon.FinalistPolygon,
            visualization_elements.TextBoxNearbySearchArea: typed_polygon.NearbySearchPolygon,
            visualization_elements.TextBoxScanArea: typed_polygon.ScanAreaPolygon
        }

        self.poly_create_functions_by_type = {
            visualization_elements.Line: self._create_line_polygon,
            visualization_elements.CityScatter: self._create_scatter_polygon,
            visualization_elements.TextBoxScan: self._create_rectangle_polygon,
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
        poly_type = self.vis_element_to_poly_type_map[vis_element_type]
        try:
            poly = func(**kwargs)
            t_poly = poly_type(poly=poly)
            return t_poly
        except TypeError:
            logging.error(f"Error when attempting to create polygon from arguments:\n{kwargs}")
            raise TypeError

    def _create_line_polygon(self, line_element: visualization_elements.Line) -> typed_polygon.LinePolygon:
        x_data = line_element.algorithm_x_data
        y_data = line_element.algorithm_y_data

        slope = (y_data[1] - y_data[0]) / (x_data[1] - x_data[0])
        perpendicular_slope = -1 / slope

        poly_coords = []
        for coord in [x_data, y_data]:
            new_coord_0 = helper_functions.move_coordinate(coord[0], coord[1], slope=perpendicular_slope,
                                                           distance=line_element.algorithm_line_width / 2)
            new_coord_1 = helper_functions.move_coordinate(coord[0], coord[1], slope=-perpendicular_slope,
                                                           distance=line_element.algorithm_line_width / 2)
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

    def _create_scatter_polygon(self, vis_element: visualization_elements.VisualizationElement, radius,
                                num_points=100) -> typed_polygon.ScatterPolygon:
        angles = np.linspace(0, 2 * np.pi, num_points)
        points = [(vis_element.coord[0] + radius * np.cos(angle), vis_element.coord[1] + radius * np.sin(angle)) for
                  angle in angles]
        poly = Polygon(points)
        scatter_poly = typed_polygon.ScatterPolygon(poly=poly)
        return scatter_poly

    @staticmethod
    def _has_attributes(obj, attributes: list[str]) -> bool:
        return all(hasattr(obj, attr) for attr in attributes)

    @staticmethod
    def _get_attributes(obj, attributes: list[str]) -> tuple:
        return tuple(getattr(obj, attr) for attr in attributes)

    def _create_rectangle_polygon(self, vis_element: visualization_elements.VisualizationElement) -> Polygon:
        attributes_1 = ['lon', 'lat', 'width', 'height']
        attributes_2 = ['center_coord', 'poly_width']
        attributes_3 = ['x_min', 'y_min', 'x_max', 'y_max']
        if self._has_attributes(vis_element, attributes_1):
            lon, lat, width, height = self._get_attributes(vis_element, attributes_1)
            x_min = lon - width
            x_max = lon + width
            y_min = lat - height
            y_max = lat + height
        elif self._has_attributes(vis_element, attributes_2):
            center_coord, poly_width = self._get_attributes(vis_element, attributes_2)
            x_min = center_coord[0] - poly_width
            x_max = center_coord[0] + poly_width
            y_min = center_coord[1] - poly_width
            y_max = center_coord[1] + poly_width
        elif self._has_attributes(vis_element, attributes_3):
            x_min, y_min, x_max, y_max = self._get_attributes(vis_element, attributes_3)
        else:
            raise ValueError(f"Could not find attributes in this visualization element to create a rectangle polygon:"
                             f"\n{vis_element.__dict__}")

        coordinates = [
            (x_min, y_min),  # Bottom-left corner
            (x_max, y_min),  # Bottom-right corner
            (x_max, y_max),  # Top-right corner
            (x_min, y_max),  # Top-left corner
            (x_min, y_min)  # Closing the polygon by returning to the start
        ]

        # Create and return the Polygon
        return Polygon(coordinates)
