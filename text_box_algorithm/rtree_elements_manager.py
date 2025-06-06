
import itertools

from rtree import index

from visual_elements.element_classes import VisualElement


class RtreeVisualElementsMap:

    def __init__(self):
        self._rtree_idx = index.Index()

        self._elements = {}
        self._poly_idx_counter = itertools.count()

    def add_visual_element(self, visual_element: VisualElement):
        poly = visual_element.polygon
        poly_idx = next(self._poly_idx_counter)
        self._rtree_idx.insert(poly_idx, poly.bounds, obj=poly)
        self._elements[poly_idx] = visual_element

    def determine_nearest(self, query_poly, elements_to_ignore: list) -> dict[VisualElement: float]:
        nearest_ids = list(self._rtree_idx.nearest(query_poly.bounds, 15))

        nearby_eles = [self._elements[idx] for idx in nearest_ids
                       if self._elements[idx] not in elements_to_ignore]

        distances = {nearby_ele: nearby_ele.distance(query_poly) for nearby_ele in nearby_eles}
        return distances

