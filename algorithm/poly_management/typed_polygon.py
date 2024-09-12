from shapely import Polygon


class TypedPolygon:

    def __init__(self, poly: Polygon, poly_type: str, **kwargs):
        self.poly = poly
        a_poly_types = ('text', 'scatter', 'line')
        if poly_type not in a_poly_types:
            raise ValueError(f"Poly type '{poly_type}' not one of acceptable values {a_poly_types}")
        self.poly_type = poly_type

        self.poly_details = kwargs

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
        return self.poly.distance(other)

    def intersects(self, other_poly):
        return self.poly.intersects(other_poly)
