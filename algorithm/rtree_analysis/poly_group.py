from shapely import Polygon


class PolyGroup:

    def __init__(self, poly: Polygon, interseting_polys: list[Polygon] = None):
        self.poly = poly
        self.intersecting_polys = interseting_polys if interseting_polys else []

    def add_intersecting_polys(self, intersecting_polys: list[Polygon]):
        self.intersecting_polys.extend(intersecting_polys)
