from abc import ABC
from shapely import Polygon


class TypedPolygon(ABC):

    def __init__(self, poly: Polygon, **kwargs):
        self.poly = poly

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def bounds(self):
        return self.poly.bounds

    @property
    def centroid(self):
        return self.poly.centroid

    @property
    def exterior(self):
        return self.poly.exterior

    def distance(self, other_poly):
        if isinstance(other_poly, TypedPolygon):
            other_poly = other_poly.poly
        return self.poly.distance(other_poly)

    def intersects(self, other_poly):
        while not isinstance(other_poly, Polygon):
            other_poly = other_poly.poly
        return self.poly.intersects(other_poly)

    def has_one_of_attributes(self, attributes: dict):
        for attribute, value in attributes.items():
            if getattr(self, attribute, False) == value:
                return True


class LinePolygon(TypedPolygon):

    def __init__(self, poly: Polygon, **kwargs):
        super().__init__(poly, **kwargs)


class ScatterPolygon(TypedPolygon):

    def __init__(self, poly: Polygon, **kwargs):
        super().__init__(poly, **kwargs)


class TextBoxPolygon(TypedPolygon):

    def __init__(self, poly: Polygon, **kwargs):
        super().__init__(poly, **kwargs)


class ScanPolygon(TypedPolygon):

    def __init__(self, poly: Polygon, city_name: str, intersecting_polygons: list[TypedPolygon] = None, **kwargs):
        super().__init__(poly, **kwargs)

        self.city_name = city_name
        self.intersecting_polygons = intersecting_polygons

    def type_present_in_intersecting_polygons(self, poly_types: list[TypedPolygon]):
        for poly in self.intersecting_polygons:
            if type(poly) in poly_types:
                return True

        return False


class ScanAreaPolygon(TypedPolygon):

    def __init__(self, poly: Polygon, **kwargs):
        super().__init__(poly, **kwargs)


class FinalistPolygon(TypedPolygon):

    def __init__(self, poly: Polygon, **kwargs):
        super().__init__(poly, **kwargs)


class NearbySearchPolygon(TypedPolygon):

    def __init__(self, poly: Polygon, **kwargs):
        super().__init__(poly, **kwargs)



