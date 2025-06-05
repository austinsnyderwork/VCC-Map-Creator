import visual_elements


class CityTextBoxManager:

    def __init__(self):
        self.city_text_box_polygons: list[visual_elements.CityTextBox] = []

    def _group_city_text_boxes_by_number_of_intersctions(self):
        city_text_box_polygonss_intersections = {}
        for city_text_box_polygons in self.city_text_box_polygons:
            num_intersections = len(city_text_box_polygons.intersecting_polygons)
            if num_intersections not in city_text_box_polygonss_intersections:
                city_text_box_polygonss_intersections[num_intersections] = []
            city_text_box_polygonss_intersections[num_intersections].append(city_text_box_polygons)
        return city_text_box_polygonss_intersections

    def get_least_intersecting_city_text_boxes(self, poly_attributes_to_omit: dict, poly_types_to_omit: list[str]):
        if len(self.city_text_box_polygons) == 0:
            return []

        met_omit_condition = False
        poly_groups = []
        city_text_box_polygons_intersections = self._group_city_text_boxes_by_number_of_intersctions()
        intersections = sorted(list(city_text_box_polygons_intersections.keys()))
        for intersection_num in intersections:
            for city_text_box_polygons in city_text_box_polygons_intersections[intersection_num]:
                if not city_text_box_polygons.types_present_in_polys(poly_types_to_omit) and not city_text_box_polygons.attributes_present_in_polys(poly_attributes_to_omit):
                    poly_groups.append(city_text_box_polygons)
                    met_omit_condition = True
            if met_omit_condition:
                return poly_groups

        return city_text_box_polygons_intersections[intersections[0]]

