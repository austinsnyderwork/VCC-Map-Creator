from shapely import Polygon

from .typed_polygon import TypedPolygon



class ScanPoly(TypedPolygon):

    def __init__(self, poly: Polygon, poly_class: str, city_name: str, intersecting_polys: list[TypedPolygon] = None):
        super().__init__(poly, poly_type='scan', poly_class=poly_class)
        self.intersecting_polys = intersecting_polys if intersecting_polys else []
        self.city_name = city_name

        self.nearby_search_poly = None
        self.nearby_polys = []
        self.score = None

    def types_present_in_polys(self, poly_types: list[str]):
        for poly in self.intersecting_polys:
            if poly.poly_type in poly_types:
                return True

        return False

    def attributes_present_in_polys(self, poly_attributes: dict):
        for poly in self.intersecting_polys:
            for attribute, value in poly_attributes.items():
                if hasattr(poly, attribute):
                    if getattr(poly, attribute) == value:
                        return True

        return False

    @property
    def bounds(self):
        return self.poly.bounds

    @property
    def centroid(self):
        return self.poly.centroid

    @property
    def exterior(self):
        return self.poly.exterior

    def distance(self, other):
        while not isinstance(other, Polygon):
            other = other.poly
        return self.poly.distance(other)


