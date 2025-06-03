from polygons import polygon_functions


class AlgorithmPolygonsManagement:


    def _create_city_text_boxes_surrounding_city(self) -> list[CityTextBox]:
        city_scatter_bounds = polygon_functions.get_poly_bounds(self.city_scatter_element.algorithm_poly)
        city_box = box_geometry.BoxGeometry(dimensions=city_scatter_bounds)
        city_box.add_buffer(self.city_buffer)

        algorithm_functions.orient_text_box_for_algorithm_start(text_box=self.text_box,
                                                                city_box=city_box)
        city_perimeter = (2 * city_box.height) + (2 * city_box.width)
        perimeter_movement_amount = city_perimeter / self.number_of_search_steps

        city_text_boxes = []

        box_width = self.text_box.x_max - self.text_box.x_min
        box_height = self.text_box.y_max - self.text_box.y_min

        while self.text_box.x_min < city_box.x_max:
            scan_poly = self.poly_factory.create_polygon(box=self.text_box,
                                                         vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('right', min(perimeter_movement_amount, box_width), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        while self.text_box.y_min < city_box.y_max:
            scan_poly = self.poly_factory.create_polygon(box=self.text_box,
                                                         vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('up', min(perimeter_movement_amount, box_height), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        while self.text_box.x_max > city_box.x_min:
            scan_poly = self.poly_factory.create_polygon(box=self.text_box,
                                                         vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('left', min(perimeter_movement_amount, box_width), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        while self.text_box.y_max > city_box.y_min:
            scan_poly = self.poly_factory.create_polygon(box=self.text_box,
                                                         vis_element_type=CityTextBox)
            city_text_box = CityTextBox(algorithm_poly=scan_poly,
                                        city_name=self.city_name,
                                        site_type=self.city_scatter_element.site_type)
            polygons.move_poly('down', min(perimeter_movement_amount, box_height), dimensions=self.text_box.dimensions)
            city_text_boxes.append(city_text_box)

        return city_text_boxes
