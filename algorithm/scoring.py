from .poly_management import ScanPoly
from .spatial_analysis_functions import get_distance_between_elements

class ScanPolyScores:

    def __init__(self, scan_poly: ScanPoly, poly_distances: list[float], ):
        self.scan_poly = scan_poly

def _get_scan_poly_nearby_distances(city_poly, scan_poly: ScanPoly):
    distances = [get_distance_between_elements(scan_poly.poly, intersecting_poly)
                 for intersecting_poly in scan_poly.intersecting_polys]
    city_distance = get_distance_between_elements(city_poly, scan_poly.poly)
    return {
        'poly_distances': distances,
        'city_distance': city_distance
    }

def score_distances(distances: dict):

def normalize


def score_scan_polys(city_poly, scan_polys: list[ScanPoly]):
    distances = {
        'poly_distances': [],
        'city_distances': []
    }
    for scan_poly in scan_polys:
        scan_poly_distances = _get_scan_poly_nearby_distances(city_poly=city_poly,
                                                              scan_poly=scan_poly)
        distances['poly_distances'].append(scan_poly_distances['poly_distances'])
        distances['city_distances'].append(scan_poly_distances['city_distance'])

    poly_groups_by_score = {}
    for



