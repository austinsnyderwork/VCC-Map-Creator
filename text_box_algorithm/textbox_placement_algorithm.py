import heapq
import math

import numpy as np

from shared.rtree_elements_manager import RtreeVisualElementsMap
from shared.shared_utils import Coordinate
from visual_elements.element_classes import AlgorithmClassification, CityScatter, TextBox, Line
from visual_elements.elements_factories import TextBoxFactory


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


class _Finalists:

    def __init__(self):
        self._finalist_scores = dict()

    @property
    def finalists(self) -> list[TextBox]:
        return list(self._finalist_scores.values())

    def add_result(self,
                   num_intersections: int,
                   element_distances: dict,
                   text_box
                   ):
        distances_to_invalids = [
            d for ele, d in element_distances.items()
            if isinstance(ele, (CityScatter, TextBox))
        ]
        shortest_distance_to_invalid = min(distances_to_invalids) if distances_to_invalids else float('inf')

        all_distances = list(element_distances.values())
        shortest_distance_to_element = max(min(all_distances), 1e-6)

        distance_to_invalid_score = shortest_distance_to_invalid ** 2
        distance_to_element_score = shortest_distance_to_element
        num_intersections_modifier = 1 + num_intersections

        score = (distance_to_invalid_score * distance_to_element_score) / num_intersections_modifier

        self._finalist_scores[score] = text_box

    def fetch_best(self, num_best: int = 1) -> list[TextBox]:
        top_scores = heapq.nlargest(num_best, self._finalist_scores.keys())
        return [self._finalist_scores[score] for score in top_scores]


class TextboxPlacementAlgorithm:

    def __init__(self,
                 number_of_search_steps: int,
                 rtree_map: RtreeVisualElementsMap
                 ):
        self._number_of_search_steps = number_of_search_steps

        self._rtree_map = rtree_map

    @staticmethod
    def _create_surrounding_text_boxes(city_scatter: CityScatter,
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
        city_text_boxes = self._create_surrounding_text_boxes(text_box=text_box,
                                                              city_scatter=city_scatter)

        finalists = _Finalists()
        for city_text_box in city_text_boxes:
            yield [city_text_box], AlgorithmClassification.TEXT_SCAN

            intersecting_elements = self._rtree_map.determine_intersecting_visual_elements(
                visual_element=city_text_box,
                elements_to_exclude=[city_scatter]
            )

            invalid_elements = [ve for ve in intersecting_elements if not isinstance(ve, Line)]

            # Unacceptable to intersect any CityScatter or TextBox
            if invalid_elements:
                # print(f"Intersecting invalid elements{'\n\t'.join(f"{type(ie)}_{ie.city_name}" for ie in invalid_elements)}")
                yield invalid_elements, AlgorithmClassification.INTERSECT
                continue

            element_distances = self._rtree_map.determine_visual_element_distances(query_poly=city_text_box.polygon,
                                                                                   elements_to_ignore=[city_scatter],
                                                                                   num_elements=20)

            finalists.add_result(
                num_intersections=len(intersecting_elements),
                element_distances=element_distances,
                text_box=city_text_box
            )

        if not finalists.finalists:
            raise ValueError(f"No finalists found for {str(city_scatter)}")

        yield finalists.fetch_best(num_best=3), AlgorithmClassification.TEXT_FINALIST
        yield finalists.fetch_best(num_best=1), AlgorithmClassification.TEXT_BEST
