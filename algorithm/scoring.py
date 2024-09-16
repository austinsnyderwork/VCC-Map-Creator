import logging
import numpy as np

from .poly_management import ScanPolyAndIntersections
from .spatial_analysis_functions import get_distance_between_elements



def _get_scan_poly_intersections_distances(scan_poly_intersections: ScanPolyAndIntersections):
    distances = [get_distance_between_elements(scan_poly_intersections.scan_poly, intersecting_poly)
                 for intersecting_poly in scan_poly_intersections.intersecting_polys]
    city_distance = get_distance_between_elements(search_poly, poly_group.scan_poly)
    return {
        'poly_distances': distances,
        'city_distance': city_distance
    }

def score_poly_intersections(scan_poly_intersections: list[ScanPolyAndIntersections]):
    scan_intersections_scores = {}
    for scan_intersections_obj in scan_poly_intersections:
        distances = _get_scan_poly_intersections_distances(scan_poly_intersections)
        poly_distance_scores.extend(distances['poly_distances'])
        city_distance_scores.append(distances['city_distance'])

    poly_groups_by_score = {}
    for



