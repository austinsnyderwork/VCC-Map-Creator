import itertools

from rtree import index

from visual_elements.element_classes import VisualElement


class RtreeVisualElementsMap:

    def __init__(self):
        self.rtree_ = index.Index()

        self._elements = dict()
        self._poly_idx_counter = itertools.count()

    @property
    def elements(self) -> list:
        return list(self._elements.values())

    def add_visual_element(self, visual_element: VisualElement):
        poly = visual_element.polygon
        poly_idx = next(self._poly_idx_counter)
        self.rtree_.insert(poly_idx, poly.bounds, obj=poly)
        self._elements[poly_idx] = visual_element

    def fetch_visual_elements(self,
                              indices,
                              elements_to_exclude):
        return [self._elements[idx] for idx in indices
                if self._elements[idx] not in elements_to_exclude]

    def determine_visual_element_distances(self,
                                           query_poly,
                                           elements_to_ignore: list,
                                           num_elements) -> dict[VisualElement: float]:
        nearest_ids = list(self.rtree_.nearest(query_poly.bounds, num_elements))

        nearby_eles = self.fetch_visual_elements(indices=nearest_ids,
                                                 elements_to_exclude=elements_to_ignore)

        distances = {nearby_ele: nearby_ele.polygon.distance(query_poly) for nearby_ele in nearby_eles}
        return distances

    def _determine_intersecting_bounding_boxes(self,
                                               visual_element: VisualElement
                                               ):
        indices = list(self.rtree_.intersection(visual_element.polygon.bounds))
        ves = [self._elements[idx] for idx in indices]
        return ves

    def determine_intersecting_visual_elements(self,
                                               visual_element: VisualElement,
                                               elements_to_exclude: list = None
                                               ) -> list:
        elements_to_exclude = elements_to_exclude or []

        intersecting_bboxes = self._determine_intersecting_bounding_boxes(visual_element)

        # Ignore the city scatter since we know we don't intersect that
        vis_elements = [ve for ve in intersecting_bboxes if ve not in elements_to_exclude]

        # Check whether it actually intersects
        vis_elements = [ve for ve in vis_elements if visual_element.polygon.intersects(ve.polygon)]

        return vis_elements
