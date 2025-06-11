from polygons.polygon_factory import PolygonFactory
from shared.shared_utils import Coordinate
from .element_classes import TextBox


class TextBoxFactory:
    
    @staticmethod
    def create_text_box(center_coord: Coordinate,
                        text_box_width: float,
                        text_box_height: float,
                        map_attributes: dict = None,
                        algo_attributes: dict = None):
        center_x, center_y = center_coord.lon_lat

        x_min = center_x - (text_box_width / 2)
        x_max = center_x + (text_box_width / 2)

        y_min = center_y - (text_box_height / 2)
        y_max = center_y + (text_box_height / 2)

        poly = PolygonFactory.create_rectangle(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max
        )
        new_text_box = TextBox(
            width=text_box_width,
            height=text_box_height,
            polygon=poly,
            map_attributes=map_attributes,
            algo_attributes=algo_attributes
        )

        return new_text_box
    