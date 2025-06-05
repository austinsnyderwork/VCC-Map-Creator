
import itertools

from rtree import index

from visualization_elements.element_classes import VisualizationElement


class RtreeElementsManager:

    def __init__(self):
        self._rtree_idx = index.Index()

        self._elements = {}
        self._poly_idx_counter = itertools.count()

    @staticmethod
    def _generate_poly_key(poly):
        return (poly,)

    def add_visualization_element(self,
                                  visualization_element: VisualizationElement):
        poly = visualization_element.polygon
        poly_idx = next(self._poly_idx_counter)
        self._rtree_idx.insert(poly_idx, poly.bounds, obj=poly)
        self._elements[poly_idx] = visualization_element

    def determine_nearest_elements(self, query_poly, elements_to_ignore: list) -> dict:
        nearest_ids = list(self._rtree_idx.nearest(query_poly.bounds, 15))
        elements = {idx: self._elements[idx] for idx in nearest_ids
                    if self._elements[idx] not in elements_to_ignore}
        distances = {nearby_ele.distance(query_poly): nearby_ele for nearby_ele in elements}
        return distances

