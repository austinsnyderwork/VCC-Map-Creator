from .scan_poly import ScanPoly


class ScanPolysManager:

    def __init__(self):
        self._poly_types = {}

        self.scan_poly_intersections = {}

    def add_scan_poly(self, scan_poly: ScanPoly):
        num_intersections = len(scan_poly.intersecting_polys)
        if num_intersections not in self.scan_poly_intersections:
            self.scan_poly_intersections[num_intersections] = []
        self.scan_poly_intersections[num_intersections].append(scan_poly)

    def get_least_intersections_poly_groups(self, poly_attributes_to_omit: dict, poly_types_to_omit: list[str]):
        met_omit_condition = False
        poly_groups = []
        intersections = sorted(list(self.scan_poly_intersections.keys()))
        for intersection_num in intersections:
            for scan_poly in self.scan_poly_intersections[intersection_num]:
                if not scan_poly.types_present_in_polys(poly_types_to_omit) and not scan_poly.attributes_present_in_polys(poly_attributes_to_omit):
                    poly_groups.append(scan_poly)
                    met_omit_condition = True
            if met_omit_condition:
                return poly_groups
        if len(self.scan_poly_intersections) == 0:
            return []

        return self.scan_poly_intersections[intersections[0]]

