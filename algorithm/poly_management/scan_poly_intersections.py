from .typed_polygon import TypedPolygon


class ScanPolyIntersections:

    def __init__(self, scan_poly: TypedPolygon, intersecting_polys: list[TypedPolygon] = None):
        self.scan_poly = scan_poly
        self.intersecting_polys = intersecting_polys if intersecting_polys else []

        self.nearest_polys = []

    def add_intersecting_polys(self, intersecting_polys: list[TypedPolygon]):
        self.intersecting_polys.extend(intersecting_polys)

    def types_present_in_polys(self, check_types: list[str]):
        for poly in self.intersecting_polys:
            if poly.poly_type in check_types:
                return True
