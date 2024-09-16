from shapely import Point
from .scan_poly_and_intersections import ScanPolyAndIntersections


class ScanPolyIntersectionsManager:

    def __init__(self):
        self._poly_types = {}

        self.scan_poly_intersections = {}

    def add_scan_poly_intersections(self, scan_poly_intersections: ScanPolyAndIntersections):
        num_intersections = len(scan_poly_intersections.intersecting_polys)
        if num_intersections not in self.scan_poly_intersections:
            self.scan_poly_intersections[num_intersections] = []
        self.scan_poly_intersections[num_intersections].append(scan_poly_intersections)

    def get_least_intersections_poly_groups(self, poly_types_to_omit: list[str]):
        met_omit_condition = False
        poly_groups = []
        intersections = sorted(list(self.scan_poly_intersections.keys()))
        for intersection_num in intersections:
            for poly_group in self.scan_poly_intersections[intersection_num]:
                if not poly_group.types_present_in_polys(poly_types_to_omit):
                    poly_groups.append(poly_group)
                    met_omit_condition = True
            if met_omit_condition:
                return poly_groups

        return self.scan_poly_intersections[intersections[0]]

