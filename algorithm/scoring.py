import logging
import numpy as np

from .algo_utils import poly_result
from .poly_management import ScanPoly
from algorithm import spatial_analysis


def normalize_value(value, old_min, old_max, new_min, new_max):
    # Handle edge case where old_max == old_min
    if old_max == old_min:
        return new_min
    return new_min + (value - old_min) * (new_max - new_min) / (old_max - old_min)


def normalize_distances(distances, old_min, old_max, new_min, new_max):
    return [normalize_value(d, old_min, old_max, new_min, new_max) for d in distances]


class ScanPolyScore:

    def __init__(self, scan_poly: ScanPoly, poly_distances: list[float], city_distance: float):
        self.scan_poly = scan_poly

        self.poly_distances = poly_distances
        self.city_distance = city_distance

        self.norm_city_distance = -1
        self.norm_poly_distances = []


def _get_scan_poly_nearby_distances(city_poly, scan_poly: ScanPoly):
    distances = [spatial_analysis.get_distance_between_elements(scan_poly, nearby_poly)
                 for nearby_poly in scan_poly.nearby_polys]
    city_distance = spatial_analysis.get_distance_between_elements(city_poly, scan_poly)
    return {
        'poly_distances': distances,
        'city_distance': city_distance
    }


def _score(scan_poly_score: ScanPolyScore):
    default_score = 1e15

    if len(scan_poly_score.poly_distances) == 0:
        return default_score

    # We want the city distance to be weighted higher than the poly distances
    city_distance_score = 2 * (1 / (scan_poly_score.norm_city_distance + 1e-5))
    logging.info(f"City distance: {scan_poly_score.norm_city_distance} | City score: {city_distance_score}")
    weighted_poly_distances = [1 / (d ** 1.5 + 1e-10) for d in scan_poly_score.norm_poly_distances]
    poly_distances_score = sum(weighted_poly_distances) / len(weighted_poly_distances)
    score = city_distance_score * poly_distances_score
    logging.info(f"Score for poly finalist: City Distance ({city_distance_score}) * "
                 f"Nearby Poly Distances({poly_distances_score}) = {score}")
    scan_poly_score.scan_poly.score = score
    return score


def score_scan_polys(city_poly, scan_polys: list[ScanPoly]):
    logging.info(f"Scoring scan polys for {city_poly.city_name}")
    scan_poly_scores = []
    near_poly_distances = []
    for scan_poly in scan_polys:
        scan_poly_distances = _get_scan_poly_nearby_distances(city_poly=city_poly,
                                                              scan_poly=scan_poly)
        near_poly_distances.extend(scan_poly_distances['poly_distances'])
        scan_poly_score = ScanPolyScore(scan_poly=scan_poly,
                                        poly_distances=scan_poly_distances['poly_distances'],
                                        city_distance=scan_poly_distances['city_distance'])
        scan_poly_scores.append(scan_poly_score)
    logging.info(f"\tThere are {len(near_poly_distances)} nearby polys total for all scan polys for this city.")
    if len(near_poly_distances) == 0:
        for scan_poly_score in scan_poly_scores:
            city_distance = 2 * (1 / (scan_poly_score.city_distance + 1e-10))
            scan_poly_score.scan_poly.score = city_distance
        return

    city_distances = [scan_poly_score.city_distance for scan_poly_score in scan_poly_scores]
    city_distances_min = min(city_distances)
    city_distances_max = max(city_distances)
    for scan_poly_score in scan_poly_scores:
        scan_poly_score.norm_city_distance = normalize_value(value=scan_poly_score.city_distance,
                                                             old_min=city_distances_min,
                                                             old_max=city_distances_max,
                                                             new_min=0,
                                                             new_max=1)

    near_poly_distances_min = min(near_poly_distances)
    near_poly_distances_max = max(near_poly_distances)
    for scan_poly_score in scan_poly_scores:
        scan_poly_score.norm_poly_distances = normalize_distances(distances=scan_poly_score.poly_distances,
                                                                  old_min=near_poly_distances_min,
                                                                  old_max=near_poly_distances_max,
                                                                  new_min=0,
                                                                  new_max=1)
    max_score = -1
    for i, scan_poly_score in enumerate(scan_poly_scores):
        new_score = _score(scan_poly_score)
        new_max = new_score > max_score
        max_score = new_score if new_max else max_score
        finalist_result = poly_result.PolyResult(poly=scan_poly_score.scan_poly,
                                                 poly_type='finalist',
                                                 num_iterations=i,
                                                 new_max_score=new_max)
        yield finalist_result
        nearby_scan_result = poly_result.PolyResult(poly=scan_poly_score.scan_poly.nearby_search_poly,
                                                    poly_type='nearby_search',
                                                    num_iterations=i,
                                                    new_max_score=new_max)
        yield nearby_scan_result
