from .poly_group import PolyGroup


class PolyGroupsManager:

    def __init__(self):
        self._poly_types = {}

        self._poly_group_intersections = {}

    def add_poly_group(self, poly_group: PolyGroup):
        num_intersections = len(poly_group.intersecting_polys)
        if num_intersections not in self._poly_group_intersections:
            self._poly_group_intersections[num_intersections] = []
        self._poly_group_intersections[num_intersections].append(poly_group)

    def get_least_intersections_poly_groups(self, poly_types_to_omit: list[str]):
        met_omit_condition = False
        poly_groups = []
        intersections = sorted(list(self._poly_group_intersections.keys()))
        for intersection_num in intersections:
            for poly_group in self._poly_group_intersections[intersection_num]:
                if not poly_group.types_present_in_polys(poly_types_to_omit):
                    poly_groups.append(poly_group)
                    met_omit_condition = True
            if met_omit_condition:
                return poly_groups

        return self._poly_group_intersections[intersections[0]]
