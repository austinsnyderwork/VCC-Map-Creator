import shapely
from rtree import index


def _should_omit_poly(poly, attributes_to_omit: dict):
    for attribute, value in attributes_to_omit.items():
        if getattr(poly, attribute, -9999) == value:
            return True
    return False


class RtreeAnalyzer:

    def __init__(self):
        self.rtree_idx = index.Index()

        self.visualization_elements = {}
        self.poly_idx = 0

    @staticmethod
    def _generate_poly_key(poly):
        return (poly,)

    def add_visualization_element(self, visualization_element):
        poly = visualization_element.poly
        self.rtree_idx.insert(self.poly_idx, poly.bounds, obj=poly)
        self.visualization_elements[self.poly_idx] = visualization_element
        self.poly_idx += 1

    def get_visualization_element(self, idx: int):
        return self.visualization_elements[idx]

    def get_closest_polygons(self, query_poly, attributes_to_omit: dict):
        nearest_ids = list(self.rtree_idx.nearest(query_poly.bounds, 8))
        nearby_polygons = [self.polygons[idx] for idx in nearest_ids]
        distances = {}
        for nearby_poly in nearby_polygons:
            if _should_omit_poly(nearby_poly, attributes_to_omit):
                continue
            distance = nearby_poly.distance(query_poly)
            if distance not in distances:
                distances[distance] = []
            distances[distance].append(nearby_poly)
        closest_distance = min(list(distances.keys()))
        closest_polys = distances[closest_distance]
        return closest_distance, closest_polys


