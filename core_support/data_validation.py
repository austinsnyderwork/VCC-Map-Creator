from collections import Counter

from entities.entity_classes import ProviderAssignment
from shared.rtree_elements_manager import RtreeVisualElementsMap
from visual_elements.element_classes import CityScatter, TextBox


def delete_same_origin_visiting_rows(df):
    df = df[df['origin_city'] != df['visiting_city']]
    return df


def verify_no_city_scatter_intersections(rtree_map: RtreeVisualElementsMap):
    city_scatters = {c for c in rtree_map.elements if isinstance(c, CityScatter)}

    for c in city_scatters:
        intersectings = rtree_map.determine_intersecting_visual_elements(visual_element=c,
                                                                         elements_to_exclude=[c])
        intersecting_scatters = [i for i in intersectings if isinstance(i, CityScatter)]
        if intersecting_scatters:
            raise ValueError(f"CityScatter {c.city_name} intersects with "
                             f"{[i.city_name for i in intersecting_scatters]}")


def verify_text_box_city_scatter_pairs(elements):
    text_cities = {ve.city_name for ve in elements
                   if isinstance(ve, TextBox)}
    scatter_cities = {ve.city_name for ve in elements
                      if isinstance(ve, CityScatter)}

    missing_scatter_cities = {city_name for city_name in text_cities if city_name not in scatter_cities}
    if missing_scatter_cities:
        raise ValueError(f"Missing CityScatter cities: {missing_scatter_cities}")

