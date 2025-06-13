import math

import numpy as np

from shared.shared_utils import Coordinate
from visual_elements.element_classes import AlgorithmClassification, CityScatter, TextBox, Line
from visual_elements.elements_factories import TextBoxFactory
from .rtree_elements_manager import RtreeVisualElementsMap


class _ScatterCircling:

    def __init__(self,
                 centroid: Coordinate,
                 radius: float):
        self.centroid = centroid
        self.radius = radius

    def _create_coordinate(self, rect_width, rect_height, angle):
        angle_rad = math.radians(angle)
        cx, cy = self.centroid.lon, self.centroid.lat

        # Circle edge at this angle
        circle_x = cx + self.radius * math.cos(angle_rad)
        circle_y = cy + self.radius * math.sin(angle_rad)

        if 0 <= angle < 90 or 270 < angle <= 360:
            x = circle_x + rect_width / 2
        elif 90 < angle < 270:
            x = circle_x - rect_width / 2
        else:
            x = circle_x

        if 0 < angle < 180:
            y = circle_y + rect_height / 2
        elif 180 < angle < 360:
            y = circle_y - rect_height / 2
        else:
            y = circle_y

        return Coordinate(longitude=x, latitude=y)

    def create_encircling_coordinates(self, rect_width, rect_height, angle_step):
        coords = []
        for angle in np.arange(0, 360, angle_step):
            new_coord = self._create_coordinate(rect_width, rect_height, angle)
            coords.append(new_coord)
        return coords

    """def create_encircling_coordinates(self, rect_width, rect_height) -> list[Coordinate]:
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
            22.5: Coordinate(

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

        return list(rect_coords.values())"""


class _Finalists:

    def __init__(self):
        self._lowest_num_intersections = float('inf')
        self._finalists = list()

    def add_result(self, num_intersections: int, text_box):
        if num_intersections < self._lowest_num_intersections:
            self._lowest_num_intersections = num_intersections
            self._finalists = [text_box]
        elif num_intersections == self._lowest_num_intersections:
            self._finalists.append(text_box)

    def fetch_finalists(self):
        return self._finalists


class TextboxPlacementAlgorithm:

    def __init__(self,
                 number_of_search_steps: int,
                 rtree_map: RtreeVisualElementsMap):
        self._number_of_search_steps = number_of_search_steps

        self._rtree_map = rtree_map

    def _get_intersecting_vis_elements(self,
                                       city_text_box: TextBox,
                                       city_scatter
                                       ) -> list:
        intersecting_bboxes = self._rtree_map.determine_intersecting_visual_elements(city_text_box)

        # Ignore the city scatter since we know we don't intersect that
        vis_elements = [ve for ve in intersecting_bboxes if ve != city_scatter]

        # Check whether it actually intersects
        vis_elements = [ve for ve in vis_elements if city_text_box.polygon.intersects(ve.polygon)]

        return vis_elements

    def _determine_best_finalist(self, finalists: list[TextBox], city_scatter):
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

        yield finalists, AlgorithmClassification.TEXT_FINALIST

        best_finalist = finalist_scores[max(list(finalist_scores))]
        yield [best_finalist], AlgorithmClassification.TEXT_BEST

    def _determine_text_box_finalists(self,
                                      city_text_boxes,
                                      city_scatter: CityScatter):
        finalists = _Finalists()
        for city_text_box in city_text_boxes:
            yield [city_text_box], AlgorithmClassification.TEXT_SCAN

            intersecting_elements = self._get_intersecting_vis_elements(city_text_box=city_text_box,
                                                                        city_scatter=city_scatter)

            invalid_elements = [ve for ve in intersecting_elements if not isinstance(ve, Line)]

            # Unacceptable to intersect any CityScatter or TextBox
            if invalid_elements:
                print(f"Invalid elements{'\n\t'.join(f"{type(ie)}_{ie.city_name}" for ie in invalid_elements)}")
                yield invalid_elements, AlgorithmClassification.INTERSECT
                continue

            finalists.add_result(
                num_intersections=len(intersecting_elements),
                text_box=city_text_box
            )

        yield finalists.fetch_finalists(), AlgorithmClassification.TEXT_FINALIST

    def _create_surrounding_text_boxes(self,
                                       city_scatter: CityScatter,
                                       text_box: TextBox
                                       ) -> list[TextBox]:
        print("Creating surrounding text boxes.")
        scatter_circling = _ScatterCircling(
            centroid=city_scatter.coord,
            radius=city_scatter.radius
        )

        rectangle_centroids = scatter_circling.create_encircling_coordinates(rect_width=text_box.width,
                                                                             rect_height=text_box.height,
                                                                             angle_step=22.5)
        text_boxes = []
        for rectangle_centroid in rectangle_centroids:
            new_text_box = TextBoxFactory.create_text_box(
                city_name=text_box.city_name,
                font=text_box.font,
                fontsize=text_box.fontsize,
                fontweight=text_box.fontweight,
                fontcolor=text_box.fontcolor,
                zorder=text_box.zorder,
                center_coord=rectangle_centroid,
                text_box_width=text_box.width,
                text_box_height=text_box.height
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

        for elements, classification in self._determine_text_box_finalists(
                city_text_boxes=city_text_boxes,
                city_scatter=city_scatter
        ):
            # We don't display finalists until we are determining the best finalist
            if classification == AlgorithmClassification.TEXT_FINALIST:
                print(f"Finalists extended: {len(elements)}")
                finalists.extend(elements)
                continue

            yield elements, classification

        if not finalists:
            raise ValueError(f"No finalists found for city {city_scatter.city_name}")

        for elements, classification in self._determine_best_finalist(finalists=finalists,
                                                                      city_scatter=city_scatter):
            yield elements, classification
