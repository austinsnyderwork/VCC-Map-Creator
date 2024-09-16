from .typed_polygon import TypedPolygon


class ScanPoly:

    def __init__(self, poly: TypedPolygon, intersecting_polys: list[TypedPolygon] = None):
        self.poly = poly
        self.intersecting_polys = intersecting_polys if intersecting_polys else []

        self.nearby_polys = []

    def types_present_in_polys(self, check_types: list[str]):
        for poly in self.intersecting_polys:
            if poly.poly_type in check_types:
                return True
