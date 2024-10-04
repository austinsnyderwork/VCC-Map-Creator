import logging

import algorithm
from algorithm import algorithm_functions, rtree_analyzer
import config_manager
from plotting import VisualizationElementResult
import polygons
from polygons import city_text_box_manager, polygon_functions, polygon_factory
from things import box_geometry, thing_converter
from things.visualization_elements import CityScatter, CityTextBox, Intersection, \
    TextBoxFinalist, Best
from things import visualization_elements


class BidirectionalDistancesDict:

    def __init__(self):
        self.distances_to_vis_elements = {}
        self.vis_elements_to_distances = {}

    def add(self, vis_element, distance):
        self.distances_to_vis_elements[distance] = vis_element
        self.vis_elements_to_distances[vis_element] = distance

    def get_vis_element(self, distance):
        return self.distances_to_vis_elements[distance]

    def get_distance(self, vis_element):
        return self.vis_elements_to_distances[vis_element]

    def get_all_vis_elements(self):
        return self.distances_to_vis_elements.values()

    def get_all_distances(self):
        return self.distances_to_vis_elements.keys()


class CityScanner:

    def __init__(self, config: config_manager.ConfigManager, text_box: box_geometry.BoxGeometry,
                 poly_factory: polygon_factory.PolygonFactory, city_scatter_element: CityScatter,
                 city_buffer: int, number_of_search_steps: int):
        self.config = config
        self.text_box = text_box
        self.city_scatter_element = city_scatter_element
        self.city_name = self.city_scatter_element.city_name
        self.poly_factory = poly_factory
        self.city_buffer = city_buffer
        self.number_of_search_steps = number_of_search_steps

        self.city_text_box_manager_ = city_text_box_manager.CityTextBoxManager()

        self.intersecting_polygon_patches = []

    @staticmethod
    def _fill_intersections_data(intersections_data, intersecting_vis_elements, city_text_box):
        num_intersections = len(intersecting_vis_elements)
        if num_intersections < intersections_data['lowest_intersections']:
            intersections_data['lowest_intersections'] = num_intersections
            intersections_data['lowest_intersection_vis_elements'] = [city_text_box]
        elif num_intersections == intersections_data['lowest_intersections']:
            intersections_data['lowest_intersection_vis_elements'].append(city_text_box)

    def _run_initial_scan(self, rtree_analyzer_: rtree_analyzer.RtreeAnalyzer):
        city_text_boxes = self._create_city_text_boxes_surrounding_city()
        ideal_lowest_intersections_data = {
            'lowest_intersections': 100,
            'lowest_intersection_vis_elements': []
        }
        all_lowest_intersections_data = {
            'lowest_intersections': 100,
            'lowest_intersection_vis_elements': []
        }
        for i, city_text_box in enumerate(city_text_boxes):
            intersecting_vis_elements = algorithm_functions.get_intersecting_vis_elements(
                rtree_analyzer_=rtree_analyzer_,
                city_text_box=city_text_box,
                ignore_elements=[
                    self.city_scatter_element])
            nonstarter_intersections = [vis_element for vis_element in intersecting_vis_elements
                                        if type(vis_element) is Best or type(vis_element) is CityScatter]
            ideal = len(nonstarter_intersections) == 0

            result = VisualizationElementResult(vis_element=city_text_box)
            yield result

            for vis_element in intersecting_vis_elements:
                intersection = thing_converter.convert_visualization_element(vis_element=vis_element,
                                                                             desired_type=Intersection,
                                                                             default_poly=vis_element.default_poly)
                result = VisualizationElementResult(vis_element=intersection,
                                                    city_text_box_iterations=i)
                yield result

            self._fill_intersections_data(all_lowest_intersections_data, intersecting_vis_elements,
                                          city_text_box)
            if ideal:
                self._fill_intersections_data(ideal_lowest_intersections_data, intersecting_vis_elements,
                                              city_text_box)

        if len(ideal_lowest_intersections_data['lowest_intersection_vis_elements']) > 0:
            lowest_intersections_vis_eles = ideal_lowest_intersections_data['lowest_intersection_vis_elements']
        else:
            lowest_intersections_vis_eles = all_lowest_intersections_data['lowest_intersection_vis_elements']
        for i, vis_element in enumerate(lowest_intersections_vis_eles):
            finalist = thing_converter.convert_visualization_element(vis_element=vis_element,
                                                                     desired_type=TextBoxFinalist,
                                                                     poly=vis_element.poly)
            result = VisualizationElementResult(vis_element=finalist,
                                                num_iterations=i)
            yield result

    def _create_city_text_boxes_surrounding_city(self) -> list[CityTextBox]:
        city_scatter_bounds = polygon_functions.get_poly_bounds(self.city_scatter_element.algorithm_poly)
        city_box = box_geometry.BoxGeometry(dimensions=city_scatter_bounds)
        city_box.add_buffer(self.city_buffer)

        algorithm_functions.move_text_box_to_bottom_left_city_box_corner(text_box=self.text_box,
                                                                         city_box=city_box)
        city_perimeter = (2 * city_box.height) + (2 * city_box.width)
        perimeter_movement_amount = city_perimeter / self.number_of_search_steps

        city_text_boxes = []

        box_width = self.text_box.x_max - self.text_box.x_min
        box_height = self.text_box.y_max - self.text_box.y_min

        while self.text_box.x_min < city_box.x_max:
            scan_poly = self.poly_factory.create_poly(box=self.text_box,
                                                      vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('right', min(perimeter_movement_amount, box_width), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        while self.text_box.y_min < city_box.y_max:
            scan_poly = self.poly_factory.create_poly(box=self.text_box,
                                                      vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('up', min(perimeter_movement_amount, box_height), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        while self.text_box.x_max > city_box.x_min:
            scan_poly = self.poly_factory.create_poly(box=self.text_box,
                                                      vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('left', min(perimeter_movement_amount, box_width), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        while self.text_box.y_max > city_box.y_min:
            scan_poly = self.poly_factory.create_poly(box=self.text_box,
                                                      vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('down', min(perimeter_movement_amount, box_height), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        return city_text_boxes

    def _find_closest_element(self, distances_data: dict, element_types, max_considered_distance: int):
        sorted_dict = {key: distances_data[key] for key in sorted(distances_data.keys())}
        for distance, vis_element in sorted_dict.items():
            if distance > max_considered_distance:
                return 1e10
            if type(vis_element) in element_types:
                return distance
        return 1e10
    def _determine_best_finalist(self, finalists: list[visualization_elements.TextBoxFinalist], rtree_analyzer_,
                                 vis_elements_to_ignore: list, polygon_to_vis_element: dict):
        all_data_dict = BidirectionalDistancesDict()
        critical_data_dict = BidirectionalDistancesDict()
        for i, finalist in enumerate(finalists):
            nearby_polygons_distances_dict = rtree_analyzer_.get_closest_visualization_elements(
                query_poly=finalist.poly,
                vis_elements_to_ignore=vis_elements_to_ignore)
            nearby_vis_elements_distances_dict = {distance: polygon_to_vis_element[polygon]
                                                  for distance, polygon in nearby_polygons_distances_dict.items()}
            closest_critical_element_distance = self._find_closest_element(nearby_vis_elements_distances_dict,
                                                                           element_types=[
                                                                               visualization_elements.CityScatter,
                                                                               visualization_elements.CityTextBox],
                                                                           max_considered_distance=100000)
            critical_data_dict.add(vis_element=finalist,
                                   distance=closest_critical_element_distance)
            all_data_dict.add(vis_element=finalist,
                              distance=min(list(nearby_vis_elements_distances_dict.keys())))
            result = VisualizationElementResult(vis_element=finalist,
                                                num_iterations=i)
            yield result

        finalist_scores = {}
        for finalist in finalists:
            all_score = all_data_dict.get_distance(finalist)
            critical_score = critical_data_dict.get_distance(finalist)
            score = all_score * (critical_score ** 2)
            finalist_scores[score] = finalist
        max_score = max(list(finalist_scores.keys()))
        best_finalist = finalist_scores[max_score]
        best = thing_converter.convert_visualization_element(vis_element=best_finalist,
                                                             desired_type=visualization_elements.Best,
                                                             site_type=self.city_scatter_element.site_type)
        result = VisualizationElementResult(vis_element=best)
        yield result

    def find_best_poly(self, rtree_analyzer_: rtree_analyzer.RtreeAnalyzer, polygon_to_vis_element: dict):
        finalists = []
        for result in self._run_initial_scan(rtree_analyzer_=rtree_analyzer_):
            # We want to wait to yield the finalist to be potentially plotted until it's actually being analyzed further
            # into the program
            if type(result.vis_element) is visualization_elements.TextBoxFinalist:
                finalists.append(result.vis_element)
            else:
                yield result

        for result in self._determine_best_finalist(finalists=finalists,
                                                    rtree_analyzer_=rtree_analyzer_,
                                                    vis_elements_to_ignore=[self.city_scatter_element],
                                                    polygon_to_vis_element=polygon_to_vis_element):
            yield result
            if type(result.vis_element) is Best:
                best_result = result

        yield best_result
