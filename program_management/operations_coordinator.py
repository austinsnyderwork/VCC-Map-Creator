import pandas as pd
from visual_elements.element_classes import TextBox, CityScatter, Line, TextBoxAttribute

from config_manager import ConfigManager
from entities.factory import EntitiesFactory
from environment_management.city_origin_networks import CityNetworksHandler
from mapping import MapDisplay
from plot_maps.base_classes import ConditionsController
from polygons.polygon_factory import PolygonFactory
from text_box_algorithm import AlgorithmDisplay
from text_box_algorithm.rtree_elements_manager import RtreeVisualElementsMap
from text_box_algorithm.textbox_placement_algorithm import TextboxPlacementAlgorithm


class OperationsCoordinator:

    def __init__(self, vcc_df: pd.DataFrame):
        self._entities_container = EntitiesFactory.create_entities(vcc_df)
        self._city_networks_handler = CityNetworksHandler().fill_networks(entities_container=self._entities_container)

        config = ConfigManager()
        self.text_box_algorithm = TextboxPlacementAlgorithm(
            rtree_map=RtreeVisualElementsMap(),
            city_buffer=config('text_box_algorithm.city_to_text_box_buffer', int),
            number_of_search_steps=config('text_box_algorithm.search_steps', int)
        )

        self._map_display = MapDisplay(
            figure_size=(config('display.fig_size_x', int), config('display.fig_size_y', int)),
            county_line_width=config('display.county_line_width', float)
        )

        self._algo_display = AlgorithmDisplay(

        )

    def create_map(self, conditions_controller: ConditionsController):
        rtree_map = RtreeVisualElementsMap()
        # 1. Determine the corresponding VisualElement for each entity
        elements = [conditions_controller.determine_visual_element(entity)
                    for entity in self._entities_container.entities]
        texts = [element for element in elements if isinstance(element, TextBox)]
        non_texts = [element for element in elements if not isinstance(element, TextBox)]

        # 2. Create a polygon for each non-TextBox entity (TextBoxes need their centroid determined by the
        # TextBoxPlacementAlgorithm). Then add the VisualElement with its new polygon into the RtreeVisualElementMap
        for non_text in non_texts:
            if isinstance(non_text, Line):
                line_poly = PolygonFactory.create_line(
                    coord_0=non_text.origin_coordinate,
                    coord_1=non_text.visiting_coordinate,
                    width=non_text.width
                )
                non_text.polygon = line_poly
            elif isinstance(non_text, CityScatter):
                scatter_poly = PolygonFactory.create_scatter(
                    coord=non_text.centroid,
                    radius=non_text.radius
                )
                non_text.polygon = scatter_poly

            self._map_display.display_element(non_text)

            rtree_map.add_visual_element(visual_element=non_text)

        # 3. Use the non-TextBox visual elements in the RTree to determine the best placement for TextBoxes
        for text in texts:
            text_box_width, text_box_height = self._map_display.get_text_box_dimensions(
                text_box=text,
                font_size=text.map_attributes[TextBoxAttribute.FONT_SIZE],
                font=text.map_attributes[TextBoxAttribute.FONT]
            )
            text.width = text_box_width
            text.height = text_box_height

            city_scatter = [nt for nt in non_texts if isinstance(nt, CityScatter) and nt.city_name == text.city_name][0]

            for element, classification in self.text_box_algorithm.find_best_poly(text_box=text,
                                                                                  city_scatter=city_scatter):
                if self._algo_display:
                    self._algo_display.display_element(vis_element=element,
                                                       classification=classification)

            poly = self.text_box_algorithm.find_best_poly(text_box=text,
                                                          city_scatter=city_scatter)
            text.polygon = poly

            rtree_map.add_visual_element(text)






