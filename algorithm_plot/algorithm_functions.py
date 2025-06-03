from polygons.polygon_factory import PolygonFactory
from polygons.polygon_utils import CoordinatePack
from . import rtree_analyzer
from visualization_elements import vis_element_classes


def get_intersecting_vis_elements(rtree_analyzer_: rtree_analyzer.RtreeAnalyzer, city_text_box: vis_element_classes.CityTextBox,
                                  ignore_elements: list[vis_element_classes.VisualizationElement] = None) -> list:
    intersection_indices = list(rtree_analyzer_.rtree_idx.intersection(city_text_box.algorithm_poly.bounds))
    intersecting_vis_elements = [rtree_analyzer_.visualization_elements[idx] for idx in intersection_indices]
    filtered_vis_elements = []
    for vis_element in intersecting_vis_elements:
        if vis_element in ignore_elements:
            continue
        filtered_vis_elements.append(vis_element)

    filtered_vis_elements = [vis_element for vis_element in filtered_vis_elements if city_text_box.algorithm_poly.intersects(vis_element.poly)]
    return filtered_vis_elements


def verify_poly(poly, name):
    if not poly.is_valid:
        raise ValueError(f"{name} poly was invalid on creation.")


def thin_poly(poly, width_adjustment: float):
    x_min, y_min, x_max, y_max = poly.bounds
    poly_width = x_max - x_min
    width_adjust_percent = width_adjustment / 100.0
    width_change = poly_width * width_adjust_percent
    x_min = x_min + (width_change / 2)
    x_max = x_max - (width_change / 2)

    coord_pack = CoordinatePack(
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max
    )

    return PolygonFactory.create_rectangle(coord_pack)

