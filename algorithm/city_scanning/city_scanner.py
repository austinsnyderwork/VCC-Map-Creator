import logging

from algorithm import helper_functions, rtree_analyzer
import config_manager
from polygons import city_text_box_manager, polygon_factory
from shapely.geometry import Polygon
from things import box_geometry, thing_converter
from things.visualization_elements.visualization_elements import CityScatter, CityTextBox, Intersection, \
    TextBoxFinalist, TextBoxNearbySearchArea, Best


class CityScanner:

    def __init__(self, config: config_manager.ConfigManager, text_box: box_geometry.BoxGeometry,
                 poly_factory: polygon_factory.PolygonFactory, city_scatter_element: CityScatter):
        self.config = config
        self.text_box = text_box
        self.city_scatter_element = city_scatter_element
        self.city_name = self.city_scatter_element.city_name
        self.poly_factory = poly_factory

        self.city_text_box_manager_ = city_text_box_manager.CityTextBoxManager()

        self.remove_polys_by_type = {
            CityTextBox: [CityTextBox, Intersection],
            TextBoxFinalist: [CityTextBox, Intersection, TextBoxFinalist, TextBoxNearbySearchArea],
            Best: [TextBoxFinalist, Intersection, TextBoxFinalist, TextBoxNearbySearchArea]
        }

        self.poly_patches = {
            Best: None,
            TextBoxNearbySearchArea: None,
            CityTextBox: None,
            TextBoxFinalist: None
        }

        self.intersecting_polygon_patches = []

    def _run_initial_scan(self, number_of_steps: int, rtree_idx, polygons, city_buffer: int):
        city_text_boxes = self._create_city_text_boxes_surrounding_city(city_buffer=city_buffer,
                                                                        number_of_steps=number_of_steps)
        lowest_intersections_data = {
            'lowest_intersections': 100,
            'lowest_intersection_vis_elements': []
        }
        for city_text_box in city_text_boxes:
            intersecting_vis_elements = helper_functions.get_intersecting_vis_elements(rtree_idx=rtree_idx,
                                                                                       polygons=polygons,
                                                                                       city_text_box=city_text_box,
                                                                                       ignore_elements=[
                                                                                           self.city_scatter_element])
            nonstarter_intersections = [vis_element for vis_element in intersecting_vis_elements
                                        if type(vis_element) is Best or type(vis_element) is CityScatter]
            if len(nonstarter_intersections) > 0:
                continue

            yield city_text_box

            for vis_element in intersecting_vis_elements:
                intersection = thing_converter.convert_visualization_element(vis_element=vis_element,
                                                                             desired_type=Intersection)
                yield intersection

            num_intersections = len(intersecting_vis_elements)
            if num_intersections < lowest_intersections_data['lowest_intersections']:
                lowest_intersections_data['lowest_intersections'] = num_intersections
                lowest_intersections_data['lowest_intersection_vis_elements'] = [city_text_box]
            elif num_intersections == lowest_intersections_data['lowest_intersections']:
                lowest_intersections_data['lowest_intersection_vis_elements'].append(city_text_box)

        for intersecting_vis_element in lowest_intersections_data['lowest_intersection_vis_elements']:
            finalist = thing_converter.convert_visualization_element(vis_element=intersecting_vis_element,
                                                                     desired_type=TextBoxFinalist)
            yield finalist

    def _create_city_text_boxes_surrounding_city(self, city_buffer: int, number_of_steps: int) -> list[CityTextBox]:
        city_box: box_geometry.BoxGeometry = self.city_scatter_element.algorithm_box_geometry
        city_box.add_buffer(city_buffer)
        helper_functions.move_text_box_to_bottom_left_city_box_corner(text_box=self.text_box,
                                                                      city_box=city_box)
        city_perimeter = (2 * city_box.height) + (2 * city_box.width)
        perimeter_movement_amount = city_perimeter / number_of_steps

        city_text_boxes = []

        while self.text_box.x_min < city_box.x_max:
            scan_poly = self.poly_factory.create_poly(poly_type='rectangle',
                                                      kwargs=self.text_box.dimensions)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name)
            self.text_box.move_box('right', min(perimeter_movement_amount, (city_box.x_max - self.text_box.x_min)))
            city_text_boxes.append(city_text_box)

        while self.text_box.y_min < city_box.y_max:
            scan_poly = self.poly_factory.create_poly(poly_type='rectangle',
                                                      kwargs=self.text_box.dimensions)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name)
            self.text_box.move_box('up', min(perimeter_movement_amount, (city_box.y_max - self.text_box.y_min)))
            city_text_boxes.append(city_text_box)

        while self.text_box.x_max > city_box.x_min:
            scan_poly = self.poly_factory.create_poly(poly_type='rectangle',
                                                      kwargs=self.text_box.dimensions)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name)
            self.text_box.move_box('left', min(perimeter_movement_amount, (self.text_box.x_max - city_box.x_min)))
            city_text_boxes.append(city_text_box)

        while self.text_box.y_max > city_box.y_min:
            scan_poly = self.poly_factory.create_poly(poly_type='rectangle',
                                                      kwargs=self.text_box.dimensions)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name)
            self.text_box.move_box('down', min(perimeter_movement_amount, (self.text_box.y_max - city_box.y_min)))
            city_text_boxes.append(city_text_box)

        return city_text_boxes

    def find_best_poly(self, rtree_analyzer_: rtree_analyzer.RtreeAnalyzer, city_buffer: int, number_of_steps: int):
        for vis_element in self._run_initial_scan(number_of_steps=number_of_steps,
                                                  rtree_idx=rtree_analyzer_.rtree_idx,
                                                  polygons=rtree_analyzer_.polygons,
                                                  city_buffer=city_buffer):
            yield vis_element
