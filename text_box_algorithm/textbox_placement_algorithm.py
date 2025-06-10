import math

from polygons.polygon_factory import PolygonFactory
from shared.shared_utils import Coordinate
from visual_elements.element_classes import TextBoxClassification, CityScatter, TextBox, Line, VisualElementClassification
from visual_elements.elements_factories import TextBoxFactory
from .rtree_elements_manager import RtreeVisualElementsMap


class _ScatterCircling:

    def __init__(self,
                 centroid: Coordinate,
                 radius: float):
        self.centroid = centroid
        self.radius = radius

    def create_encircling_coordinates(self, rect_width, rect_height) -> list[Coordinate]:
        r = self.radius
        d = r / math.sqrt(2)
        cx = self.centroid.lon
        cy = self.centroid.lat

        top_right = Coordinate(cx + d, cy + d)
        top_left = Coordinate(cx - d, cy + d)
        bottom_left = Coordinate(cx - d, cy - d)
        bottom_right = Coordinate(cx + d, cy - d)

        rect_coords = {
            0: Coordinate(
                latitude=self.centroid.lat,
                longitude=self.centroid.lon + self.radius + (rect_width / 2)
            ),
            45: Coordinate(
                latitude=top_right.lat + (rect_height / 2),
                longitude=top_right.lon + (rect_width / 2)
            ),
            90: Coordinate(
                latitude=self.centroid.lat + self.radius + (rect_height / 2),
                longitude=self.centroid.lon
            ),
            135: Coordinate(
                latitude=top_left.lat + (rect_height / 2),
                longitude=top_left.lon - (rect_width / 2)
            ),
            180: Coordinate(
                latitude=self.centroid.lat,
                longitude=self.centroid.lon - self.radius - (rect_width / 2)
            ),
            225: Coordinate(
                latitude=bottom_left.lat - (rect_height / 2),
                longitude=bottom_left.lon - (rect_width / 2)
            ),
            270: Coordinate(
                latitude=self.centroid.lat - self.radius - (rect_height / 2),
                longitude=self.centroid.lon
            ),
            315: Coordinate(
                latitude=bottom_right.lat - (rect_height / 2),
                longitude=bottom_right.lon + (rect_width / 2)
            )
        }

        return list(rect_coords.values())


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
        vis_elements = [ve for ve in vis_elements if city_text_box.polygon.intersects(ve.polygon)]

        return vis_elements

    def determine_best_finalist(self, finalists: list[TextBox], city_scatter):
        finalist_scores = dict()
        for i, finalist in enumerate(finalists):
            nearby_elements = self._rtree_map.determine_nearest(query_poly=finalist.polygon,
                                                                elements_to_ignore=[city_scatter])
            distances_to_invalids = [d for ele, d in nearby_elements.items()
                                     if isinstance(ele, CityScatter) or isinstance(ele, TextBox)]
            shortest_distance_to_invalid = min(distances_to_invalids) if distances_to_invalids else float('inf')

            all_distances = [d for ele, d in nearby_elements.items()]
            shortest_distance_to_element = min(all_distances)

            score = shortest_distance_to_element * (shortest_distance_to_invalid ** 2)
            finalist_scores[score] = finalist

        yield finalists, TextBoxClassification.FINALIST

        best_score = max(list(finalist_scores.keys()))
        yield [finalist_scores[best_score]], TextBoxClassification.BEST

    def determine_text_box_finalists(self,
                                     city_text_boxes,
                                     city_scatter: CityScatter):
        for city_text_box in city_text_boxes:
            yield [city_text_box], TextBoxClassification.SCAN

            intersecting_elements = self._get_intersecting_vis_elements(city_text_box=city_text_box,
                                                                        city_scatter=city_scatter)
            if intersecting_elements:
                yield intersecting_elements, VisualElementClassification.INTERSECT

            invalid_elements = [ve for ve in intersecting_elements if not isinstance(ve, Line)]

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
        print("Creating surrounding text boxes.")
        scatter_circling = _ScatterCircling(
            centroid=city_scatter.coord,
            radius=city_scatter.radius + self._city_buffer
        )

        rectangle_centroids = scatter_circling.create_encircling_coordinates(rect_width=text_box.width,
                                                                             rect_height=text_box.height)
        text_boxes = []
        for rectangle_centroid in rectangle_centroids:
            new_text_box = TextBoxFactory.create_text_box(center_coord=rectangle_centroid,
                                                          text_box_width=text_box.width,
                                                          text_box_height=text_box.height)
            text_boxes.append(new_text_box)

        print(f"Plotting text boxes surrounding {city_scatter.city_name} coordinate {str(city_scatter.centroid_coord)}")

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
                print(f"Finalists extended: {len(elements)}")
                finalists.extend(elements)
                continue

            yield elements, classification

        for elements, classification in self._text_box_resolver.determine_best_finalist(finalists=finalists,
                                                                                        city_scatter=city_scatter):
            yield elements, classification
