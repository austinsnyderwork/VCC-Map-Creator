from things import box_geometry

from polygons import polygon_functions
from polygons.polygon_factory import PolygonFactory
from shared.shared_utils import Direction
from visualization_elements.element_classes import TextBoxClassification, CityScatter, TextBox
from .rtree_elements_manager import RtreeElementsManager


class BestFits:

    def __init__(self):
        self._lowest_num_intersections = float('inf')
        self._best_fits = list()

        self._intersects_non_starter = True

    def add_result(self, num_intersections: int, text_box, intersects_non_starter: bool):
        # If we've found a text box that doesn't intersect a non-starter element and this text box does, then skip it
        if intersects_non_starter and not self._intersects_non_starter:
            return

        if num_intersections < self._lowest_num_intersections:
            self._lowest_num_intersections = num_intersections
            self._best_fits = [text_box]
        elif num_intersections == self._lowest_num_intersections:
            self._best_fits.append(text_box)

        if not intersects_non_starter:
            self._intersects_non_starter = False

    def fetch_best_fits(self):
        return self._best_fits


class _TextBoxCandidatesResolver:

    def __init__(self, rtree_manager: RtreeElementsManager):
        self._rtree_manager = rtree_manager

        self._best_fits = BestFits()

    def _get_intersecting_vis_elements(self,
                                       city_text_box: TextBox,
                                       city_scatter
                                       ) -> list:
        # See what elements are within the city text box Rtree bounding box
        intersection_indices = list(self._rtree_manager._rtree_idx.intersection(city_text_box.algorithm_poly.bounds))
        intersecting_vis_elements = [self._rtree_manager._elements[idx] for idx in intersection_indices]

        vis_elements = [ve for ve in intersecting_vis_elements if ve != city_scatter]

        # Check whether it actually intersects
        vis_elements = [ve for ve in vis_elements if city_text_box.algorithm_poly.intersects(ve.poly)]

        return vis_elements

    def determine_best_finalist(self, finalists: list[TextBox], city_scatter):
        finalist_scores = dict()
        for i, finalist in enumerate(finalists):
            nearby_elements = self._rtree_manager.determine_nearest_elements(query_poly=finalist.poly,
                                                                             elements_to_ignore=city_scatter)
            nearby_invalids = [d for d, ele in nearby_elements.items()
                               if isinstance(ele, CityScatter) or isinstance(ele, CityTextBox)]
            closest_invalid = min(nearby_invalids) if nearby_invalids else float('inf')

            closest_element = min([d for d, ele in nearby_elements.items()])

            score = closest_element * (closest_invalid ** 2)
            finalist_scores[score] = finalist

        best_score = max(list(finalist_scores.keys()))
        yield [finalist_scores[best_score]], TextBoxClassification.BEST

    def determine_text_box_finalists(self, city_text_boxes):
        for city_text_box in enumerate(city_text_boxes):
            yield [city_text_box], TextBoxClassification.REFERENCE

            intersecting_elements = self._get_intersecting_vis_elements(city_text_box=city_text_box)
            yield intersecting_elements, TextBoxClassification.INTERSECT

            invalid_elements = [ve for ve in intersecting_elements if not isinstance(ve, Line)]
            yield invalid_elements, TextBoxClassification.INVALID

            self._best_fits.add_result(
                num_intersections=len(intersecting_elements),
                text_box=city_text_box,
                intersects_non_starter=bool(invalid_elements)
            )

        yield self._best_fits.fetch_best_fits(), TextBoxClassification.FINALIST


class TextboxPlacementAlgorithm:

    def __init__(self,
                 rtree_manager: RtreeElementsManager,
                 city_buffer: int,
                 number_of_search_steps: int):
        self.text_box_resolver = _TextBoxCandidatesResolver(rtree_manager=rtree_manager)
        self.city_buffer = city_buffer
        self.number_of_search_steps = number_of_search_steps

        self.best_fits = BestFits()

    @staticmethod
    def _orient_text_box_for_algorithm_start(text_box: box_geometry.BoxGeometry,
                                             city_box: box_geometry.BoxGeometry):
        # Text box to the right of city box
        if text_box.x_max > city_box.x_max:
            x_distance = text_box.x_max - city_box.x_min
            text_box.move_box('left', x_distance)
        # Text box to the left of city box
        else:
            x_distance = city_box.x_min - text_box.x_max
            text_box.move_box('right', x_distance)

        # Text box above city box
        if text_box.y_max > city_box.y_max:
            y_distance = text_box.y_max - city_box.y_min
            text_box.move_box('down', y_distance)
        else:
            # Text box below city box
            y_distance = city_box.y_min - text_box.y_max
            text_box.move_box('up', y_distance)

    @staticmethod
    def _move_and_create_text_box(text_box, direction: Direction, distance, city_name):
        text_box.move(direction=direction,
                      distance=distance)
        new_poly = PolygonFactory.create_rectangle(**text_box.bounds)
        new_text_box = TextBox(poly=new_poly,
                               text=city_name)
        return new_text_box

    def _create_surrounding_text_boxes(self,
                                       city_scatter_element,
                                       text_box
                                       ) -> list[TextBox]:
        city_scatter_bounds = polygon_functions.fetch_bounds(polygon=city_scatter_element.algorithm_poly)
        city_box = BoxGeometry(dimensions=city_scatter_bounds)
        city_box.add_buffer(self.city_buffer)

        self._orient_text_box_for_algorithm_start(text_box=text_box,
                                                  city_box=city_box)

        box_width = text_box.x_max - text_box.x_min
        box_height = text_box.y_max - text_box.y_min

        city_perimeter = (2 * box_height) + (2 * box_width)
        perimeter_movement_amount = city_perimeter / self.number_of_search_steps

        city_text_boxes = []

        while text_box.x_min < city_box.x_max:
            text_box = self._move_and_create_text_box(text_box=text_box,
                                                      direction=Direction.RIGHT,
                                                      distance=min(perimeter_movement_amount, box_width),
                                                      city_name=city_name)
            city_text_boxes.append(text_box)

        while text_box.y_min < city_box.y_max:
            text_box = self._move_and_create_text_box(text_box=text_box,
                                                      direction=Direction.UP,
                                                      distance=min(perimeter_movement_amount, box_height),
                                                      city_name=city_name)
            city_text_boxes.append(text_box)

        while text_box.x_max > city_box.x_min:
            text_box = self._move_and_create_text_box(text_box=text_box,
                                                      direction=Direction.LEFT,
                                                      distance=min(perimeter_movement_amount, box_width),
                                                      city_name=city_name)
            city_text_boxes.append(text_box)

        while text_box.y_max > city_box.y_min:
            text_box = self._move_and_create_text_box(text_box=text_box,
                                                      direction=Direction.DOWN,
                                                      distance=min(perimeter_movement_amount, box_height),
                                                      city_name=city_name)
            city_text_boxes.append(text_box)

        return city_text_boxes

    def find_best_poly(self,
                       text_box: box_geometry.BoxGeometry,
                       city_scatter: CityScatter,
                       ):
        finalists = []

        city_text_boxes = self._create_surrounding_text_boxes(text_box=text_box,
                                                              city_scatter_element=city_scatter)

        for elements, classification in self.text_box_resolver.determine_text_box_finalists(city_text_boxes=city_text_boxes):
            # We don't display finalists until we are determining the best finalist
            if classification == TextBoxClassification.FINALIST:
                finalists.extend(elements)
            else:
                yield elements, classification

        for elements, classification in self.text_box_resolver.determine_best_finalist(finalists):
            yield elements, classification
