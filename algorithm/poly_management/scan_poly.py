from .typed_polygon import TypedPolygon


class ScanPoly:

    def __init__(self, poly: TypedPolygon, intersecting_polys: list[TypedPolygon] = None):
        self.poly = poly
        self.intersecting_polys = intersecting_polys if intersecting_polys else []

        self.nearby_polys = []
        self.score = -1

    def types_present_in_polys(self, check_types: list[str]):
        for poly in self.intersecting_polys:
            if poly.poly_type in check_types:
                return True

    @property
    def bounds(self):
        return self.poly.bounds

    @property
    def poly_class(self):
        return self.poly.poly_class

    @property
    def centroid(self):
        return self.poly.centroid

