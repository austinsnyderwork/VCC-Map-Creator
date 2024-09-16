from shapely import Polygon

from .typed_polygon import TypedPolygon


class ScanPoly(TypedPolygon):

    def __init__(self, poly: Polygon, poly_class: str, intersecting_polys: list[TypedPolygon] = None):
        super().__init__(poly, poly_type='scan', poly_class=poly_class)
        self.intersecting_polys = intersecting_polys if intersecting_polys else []

        self.nearby_search_poly = None
        self.nearby_polys = []
        self.score = -1

    @property
    def bounds(self):
        return self.poly.bounds

    @property
    def centroid(self):
        return self.poly.centroid

    @property
    def exterior(self):
        return self.poly.exterior

