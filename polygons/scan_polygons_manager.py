from . import typed_polygon


class ScanPolygonsManager:

    def __init__(self):
        self.scan_polygons: list[typed_polygon.ScanPolygon] = []

    def _group_scan_polygons_by_number_of_intersctions(self):
        scan_polys_intersections = {}
        for scan_poly in self.scan_polygons:
            num_intersections = len(scan_poly.intersecting_polygons)
            if num_intersections not in scan_polys_intersections:
                scan_polys_intersections[num_intersections] = []
            scan_polys_intersections[num_intersections].append(scan_poly)
        return scan_polys_intersections

    def get_least_intersecting_scan_polygons(self, poly_attributes_to_omit: dict, poly_types_to_omit: list[str]):
        if len(self.scan_polygons) == 0:
            return []

        met_omit_condition = False
        poly_groups = []
        scan_poly_intersections = self._group_scan_polygons_by_number_of_intersctions()
        intersections = sorted(list(scan_poly_intersections.keys()))
        for intersection_num in intersections:
            for scan_poly in scan_poly_intersections[intersection_num]:
                if not scan_poly.types_present_in_polys(poly_types_to_omit) and not scan_poly.attributes_present_in_polys(poly_attributes_to_omit):
                    poly_groups.append(scan_poly)
                    met_omit_condition = True
            if met_omit_condition:
                return poly_groups

        return scan_poly_intersections[intersections[0]]

