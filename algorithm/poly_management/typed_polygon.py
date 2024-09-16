from shapely import Polygon


class TypedPolygon:

    def __init__(self, poly: Polygon, poly_type: str, poly_class: str, **kwargs):
        self.poly = poly

        acceptable_poly_types = ['line', 'scatter', 'scan', 'scan_area', 'nearby_search']
        if poly_type not in acceptable_poly_types:
            raise ValueError(f"Poly type '{poly_type}' not one of acceptable values {acceptable_poly_types}.")

        accepted_poly_classes = ('text', 'scatter', 'line', 'algorithm_misc')
        if poly_class not in accepted_poly_classes:
            raise ValueError(f"Poly class '{poly_class}' not one of acceptable values {accepted_poly_classes}.")
        self.poly_class = poly_class

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
