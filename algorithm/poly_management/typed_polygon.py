from shapely import Polygon


class TypedPolygon:

    def __init__(self, poly: Polygon, poly_type: str, **kwargs):
        self.poly = poly
        self.poly_type = poly_type

        self.poly_details = kwargs

