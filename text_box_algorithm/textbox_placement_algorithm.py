import math

from polygons.polygon_factory import PolygonFactory
from shared.shared_utils import Coordinate
from visual_elements.element_classes import TextBoxClassification, CityScatter, TextBox, Line
from .rtree_elements_manager import RtreeVisualElementsMap


class _ScatterCircling:

    def __init__(self, centroid: Coordinate, radius: float):
        self.centroid = centroid
        self.radius = radius

    def get_coord_at_angle(self, angle_degrees: float) -> Coordinate:
        """Returns a Coordinate on the circle's perimeter at the given angle (in degrees)."""
        angle_radians = math.radians(angle_degrees)
        dx = self.radius * math.cos(angle_radians)
        dy = self.radius * math.sin(angle_radians)
        return Coordinate(latitude=self.centroid.lat + dy, longitude=self.centroid.lon + dx)

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

    def __init__(self, rtree_map: RtreeVisualElementsMap):
        self._rtree_map = rtree_map

        self._best_fits = BestFits()

    def _get_intersecting_vis_elements(self,
                                       city_text_box: TextBox,
                                       city_scatter
                                       ) -> list:
        # See what elements are within the city text box Rtree bounding box
        intersection_indices = list(self._rtree_map._rtree_idx.intersection(city_text_box.polygon.bounds))
        intersecting_vis_elements = [self._rtree_map._elements[idx] for idx in intersection_indices]

        vis_elements = [ve for ve in intersecting_vis_elements if ve != city_scatter]

        # Check whether it actually intersects
        vis_elements = [ve for ve in vis_elements if city_text_box.polygon.intersects(ve.poly)]

        return vis_elements

    def determine_best_finalist(self, finalists: list[TextBox], city_scatter):
        finalist_scores = dict()
        for i, finalist in enumerate(finalists):
            nearby_elements = self._rtree_map.determine_nearest(query_poly=finalist.poly,
                                                                elements_to_ignore=city_scatter)
            nearby_invalids = [d for d, ele in nearby_elements.items()
                               if isinstance(ele, CityScatter) or isinstance(ele, CityTextBox)]
            closest_invalid = min(nearby_invalids) if nearby_invalids else float('inf')

            closest_element = min([d for d, ele in nearby_elements.items()])

            score = closest_element * (closest_invalid ** 2)
            finalist_scores[score] = finalist

        best_score = max(list(finalist_scores.keys()))
        yield [finalist_scores[best_score]], TextBoxClassification.BEST

    def determine_text_box_finalists(self,
                                     city_text_boxes,
                                     city_scatter: CityScatter):
        for city_text_box in city_text_boxes:
            yield [city_text_box], TextBoxClassification.SCAN

            intersecting_elements = self._get_intersecting_vis_elements(city_text_box=city_text_box,
                                                                        city_scatter=city_scatter)
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
                 rtree_map: RtreeVisualElementsMap,
                 city_buffer: int,
                 number_of_search_steps: int):
        self._text_box_resolver = _TextBoxCandidatesResolver(rtree_map=rtree_map)
        self._city_buffer = city_buffer
        self.number_of_search_steps = number_of_search_steps

        self.best_fits = BestFits()

    def _create_surrounding_text_boxes(self,
                                       city_scatter: CityScatter,
                                       text_box: TextBox
                                       ) -> list[TextBox]:
        scatter_circling = _ScatterCircling(
            centroid=city_scatter.centroid,
            radius=city_scatter.radius + self._city_buffer
        )

        text_boxes = []
        for angle in list(range(360)):
            bottom_right_coord = scatter_circling.get_coord_at_angle(angle)
            x_min = bottom_right_coord.lon
            x_max = x_min - text_box.width

            y_min = bottom_right_coord.lat
            y_max = y_min + text_box.height

            poly = PolygonFactory.create_rectangle(
                x_min=x_min,
                x_max=x_max,
                y_min=y_min,
                y_max=y_max
            )
            new_text_box = TextBox(
                width=text_box.width,
                height=text_box.height,
                classification=TextBoxClassification.SCAN,
                polygon=poly
            )
            text_boxes.append(new_text_box)

        return text_boxes

    def find_best_poly(self,
                       text_box: TextBox,
                       city_scatter: CityScatter,
                       ):
        finalists = []

        city_text_boxes = self._create_surrounding_text_boxes(text_box=text_box,
                                                              city_scatter=city_scatter)

        for elements, classification in self._text_box_resolver.determine_text_box_finalists(
                city_text_boxes=city_text_boxes,
                city_scatter=city_scatter
        ):
            # We don't display finalists until we are determining the best finalist
            if classification == TextBoxClassification.FINALIST:
                finalists.extend(elements)
                continue

            for element in elements:
                yield element, classification

        for elements, classification in self._text_box_resolver.determine_best_finalist(finalists=finalists,
                                                                                        city_scatter=city_scatter):
            for element in elements:
                yield element, classification
