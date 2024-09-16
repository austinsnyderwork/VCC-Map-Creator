import logging
import numpy as np

from .spatial_analysis_functions import get_distance_between_elements
from algorithm.poly_management import PolyGroupsManager, PolyGroup


class Scorer:

    def __init__(self, poly_groups_manager: PolyGroupsManager):
        self.poly_groups_manager = poly_groups_manager


    def _get_poly_group_distances(self, search_poly, poly_group: PolyGroup):
        distances = [get_distance_between_elements(search_poly, intersecting_poly)
                     for intersecting_poly in poly_group.intersecting_polys]
        city_distance = get_distance_between_elements(search_poly, poly_group.scan_poly)
        return {
            'poly_distances': distances,
            'city_distance': city_distance
        }

    def find_best_poly(self, search_poly, poly_types_to_omit: list[str] = None):
        least_intersecting_poly_groups = self.poly_groups_manager.get_least_intersections_poly_groups(poly_types_to_omit)
        poly_group_scores = {}
        for poly_group in least_intersecting_poly_groups:
            distances = self._get_poly_group_distances(search_poly=search_poly,
                                                       poly_group=poly_group)
            poly_distance_scores.extend(distances['poly_distances'])
            city_distance_scores.append(distances['city_distance'])

        poly_groups_by_score = {}
        for



