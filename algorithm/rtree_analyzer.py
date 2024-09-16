
from rtree import index


class RtreeAnalyzer:

    def __init__(self):
        self.rtree_idx = index.Index()

        self.polygons = {}
        self.poly_classes = {}
        self.poly_idx = 0

    @staticmethod
    def _generate_poly_key(poly):
        return (poly,)

    def add_poly(self, poly, poly_class: str):
        self.rtree_idx.insert(self.poly_idx, poly.bounds, obj=poly)
        poly_key = self._generate_poly_key(poly=poly)
        self.polygons[self.poly_idx] = poly
        self.poly_classes[poly_key] = poly_class
        self.poly_idx += 1
