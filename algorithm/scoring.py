import logging

from .algo_utils import poly_result
from .poly_management import ScanPoly
from . import spatial_analysis


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

        self.norm_city_distance = None
        self.norm_poly_distances = []

        self.score = None
        self.force_show = None
        self.city_score = None
        self.poly_distances_scores = None


def _get_scan_poly_nearby_distances(city_poly, scan_poly: ScanPoly):
    distances = []
    for nearby_poly in scan_poly.nearby_polys:
        distances.append(spatial_analysis.get_distance_between_elements(scan_poly, nearby_poly))

    city_distance = spatial_analysis.get_distance_between_elements(city_poly, scan_poly)
    return {
        'poly_distances': distances,
        'city_distance': city_distance
    }


def _nearby_poly_is_city_associated(city_name, nearby_poly):
    if hasattr(nearby_poly, 'city_name') and nearby_poly.city_name == city_name:
        return True
    elif hasattr(nearby_poly, 'outpatient') and (nearby_poly.outpatient == city_name):
        return True
    elif hasattr(nearby_poly, 'origin') and nearby_poly.origin == city_name:
        return True

    return False


def _remove_scan_polys_without_nearby(scan_polys):
    valid_scan_polys = []
    for scan_poly in scan_polys:
        valid_nearby_polys = []
        for nearby_poly in scan_poly.nearby_polys:
            if _nearby_poly_is_city_associated(city_name=scan_poly.city_name,
                                               nearby_poly=nearby_poly):
                continue
            valid_nearby_polys.append(nearby_poly)
        if len(valid_nearby_polys) > 0:
            valid_scan_polys.append(scan_poly)
    return valid_scan_polys


def _score(scan_poly_score: ScanPolyScore):

    logging.info(f"New poly:\n\tNorm city distance: {scan_poly_score.norm_city_distance}\n\tNorm poly distances: "
                 f"{scan_poly_score.norm_poly_distances}")

    # We want the city distance to be weighted higher than the poly distances
    city_distance_score = 4 * (1 / (scan_poly_score.norm_city_distance + 1e-5))
    weighted_poly_distances = [(d ** 1.5 + 1e-10) for d in scan_poly_score.norm_poly_distances]
    poly_distances_score = sum(weighted_poly_distances) / (len(weighted_poly_distances))  # Don't divide by zero
    score = city_distance_score * poly_distances_score
    logging.info(f"\tCity Distance ({city_distance_score}) * "
                 f"Nearby Poly Distances({poly_distances_score}) = {score}")
    scan_poly_score.score = score
    # For now because the result that we yield only takes in a TypedPolygon (not ScanPolyScore), then we just attach
    # this score to the scan poly. More realistically should be a part of the ScanPolyScore, but here we are!
    scan_poly_score.scan_poly.score = score
    scan_poly_score.force_show = False
    scan_poly_score.city_score = city_distance_score
    scan_poly_score.poly_distances_scores = weighted_poly_distances


def score_scan_polys(city_poly, scan_polys: list[ScanPoly]) -> tuple:
    logging.info(f"Scoring scan polys for {city_poly.city_name}")
    scan_poly_scores = []
    near_poly_distances = []

    scan_polys = _remove_scan_polys_without_nearby(scan_polys=scan_polys)

    for scan_poly in scan_polys:
        scan_poly_distances = _get_scan_poly_nearby_distances(city_poly=city_poly,
                                                              scan_poly=scan_poly)
        near_poly_distances.extend(scan_poly_distances['poly_distances'])
        scan_poly_score = ScanPolyScore(scan_poly=scan_poly,
                                        poly_distances=scan_poly_distances['poly_distances'],
                                        city_distance=scan_poly_distances['city_distance'])
        scan_poly_scores.append(scan_poly_score)
    logging.info(f"\tThere are {len(near_poly_distances)} nearby polys total for all scan polys for this city.")

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
    for scan_poly_score in scan_poly_scores:
        _score(scan_poly_score)

    max_score = -1
    for i, scan_poly_score in enumerate(scan_poly_scores):
        if scan_poly_score.score > max_score:
            new_max_score_achieved = True
            max_score = scan_poly_score.score
            logging.info(f"!!!New max score achieved: {scan_poly_score.scan_poly.score}!!!\n"
                         f"\tWeighted poly distances:{scan_poly_score.poly_distances_scores} | "
                         f"City score: {scan_poly_score.city_score}")
        else:
            new_max_score_achieved = False
        finalist_result = poly_result.PolyResult(poly=scan_poly_score.scan_poly,
                                                 poly_type='finalist',
                                                 num_iterations=i,
                                                 new_max_score=new_max_score_achieved,
                                                 force_show=scan_poly_score.force_show)
        yield finalist_result
        nearby_scan_result = poly_result.PolyResult(poly=scan_poly_score.scan_poly.nearby_search_poly,
                                                    poly_type='nearby_search',
                                                    num_iterations=i,
                                                    new_max_score=new_max_score_achieved,
                                                    force_show=scan_poly_score.force_show)
        yield nearby_scan_result
