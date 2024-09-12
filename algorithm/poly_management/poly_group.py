from .typed_polygon import TypedPolygon


class PolyGroup:

    def __init__(self, poly: TypedPolygon, intersecting_polys: list[TypedPolygon] = None):
        self.poly = poly
        self.intersecting_polys = intersecting_polys if intersecting_polys else []

    def add_intersecting_polys(self, intersecting_polys: list[TypedPolygon]):
        self.intersecting_polys.extend(intersecting_polys)

    def types_present_in_polys(self, check_types: list[str]):
        for poly in self.intersecting_polys:
            if poly.poly_type in check_types:
                return True
