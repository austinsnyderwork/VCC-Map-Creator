import pandas as pd
from shapely import Polygon

import plotting
from config_manager import ConfigManager
from entities.factory import EntitiesFactory
from environment_management.city_origin_networks import CityNetworksHandler
from plot_maps.base_classes import ConditionsController
from plotting import AlgorithmDisplay
from polygons.polygon_factory import PolygonFactory
from text_box_algorithm.rtree_elements_manager import RtreeVisualElementsMap
from text_box_algorithm.textbox_placement_algorithm import TextboxPlacementAlgorithm, TextBoxCandidatesResolver
from visual_elements.attributes_resolver import VisualElementAttributesResolver
from visual_elements.element_classes import TextBox, CityScatter, Line, TextBoxClassification


class OperationsCoordinator:

    def __init__(self, vcc_df: pd.DataFrame):
        print("Building EntitiesContainer.")
        self._entities_container = EntitiesFactory.create_entities(vcc_df)

        print("Building CityNetworksHandler.")
        self._city_networks_handler = CityNetworksHandler().fill_networks(entities_container=self._entities_container)

        self._config = ConfigManager()
        self.text_box_algorithm = TextboxPlacementAlgorithm(
            city_buffer=self._config('algo', 'city_to_text_box_buffer', float),
            number_of_search_steps=self._config('algo', 'search_steps', int)
        )
        
        self._algo_display = None
        if self._config('algo.display', 'show_display', bool):
            self._algo_display = AlgorithmDisplay(
                figure_size=(
                    self._config('algo.display', 'fig_size_x', int),
                    self._config('algo.display', 'fig_size_y', int)
                ),
                show_pause=self._config('algo.display', 'show_pause', float),
                display_zoom_out=self._config('algo.display', 'display_zoom_out', int)
            )

    def _find_best_polygon(self,
                           rtree_map: RtreeVisualElementsMap,
                           city_scatter: CityScatter,
                           text_box: TextBox,
                           city_buffer: int,
                           number_of_steps: int) -> Polygon:
        print(f"Finding best poly for city '{city_scatter.city_name}'")

        # Center on the scan area
        if self._algo_display:
            self._algo_display.center_display(visual_element=city_scatter)

        algo = TextboxPlacementAlgorithm(
            city_buffer=city_buffer,
            number_of_search_steps=number_of_steps
        )

        candidates_resolver = TextBoxCandidatesResolver(rtree_map)
        for elements, classification in algo.find_best_poly(candidates_resolver=candidates_resolver,
                                                            text_box=text_box,
                                                            city_scatter=city_scatter):
            print(f"Algorithm plotting {len(elements)}: {classification}")
            for element in elements:
                if self._algo_display:
                    self._algo_display.plot_element(visual_element=element,
                                                    classification=classification)

                if classification == TextBoxClassification.BEST:
                    print(f"Rtree inserting Best for {text_box.city_name}")
                    rtree_map.add_visual_element(element)

                    return PolygonFactory.create_rectangle(*element.bounds)

    def create_map(self, controller_class: type(ConditionsController)):
        print("Creating map.")
        conditions_controller = controller_class(
            entities_container=self._entities_container,
            city_networks_handler=self._city_networks_handler
        )

        rtree_map = RtreeVisualElementsMap()

        # 1. Determine the corresponding VisualElement for each entity
        elements = [
            ve
            for entity in self._entities_container.entities
            for ve in conditions_controller.determine_visual_elements(entity)
        ]
        texts = [element for element in elements if isinstance(element, TextBox)]
        non_texts = [element for element in elements if not isinstance(element, TextBox)]

        print(f"ConditionsController returned {len(elements)} total elements. {len(texts)} texts and {len(non_texts)} non-texts.")

        # 2. Create a polygon for each non-TextBox entity (TextBoxes need their centroid determined by the
        # TextBoxPlacementAlgorithm). Then add the VisualElement with its new polygon into the RtreeVisualElementMap
        for non_text in non_texts:
            non_text.algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(non_text,
                                                                                               classification=None)

            # Have to fill in the polygon for each VisualElement so that it can be inserted into the Rtree
            if isinstance(non_text, Line):
                line_poly = PolygonFactory.create_line(
                    coord_0=non_text.origin_coordinate,
                    coord_1=non_text.visiting_coordinate,
                    width=non_text.algo_attributes.linewidth
                )
                non_text.polygon = line_poly
            elif isinstance(non_text, CityScatter):
                scatter_poly = PolygonFactory.create_scatter(
                    coord=non_text.coord,
                    radius=non_text.radius
                )
                non_text.polygon = scatter_poly

            rtree_map.add_visual_element(visual_element=non_text)

            if self._algo_display:
                self._algo_display.plot_element(non_text,
                                                show_display=False)

        # 3. Use the non-TextBox visual elements in the RTree to determine the best placement for TextBoxes
        for text in texts:
            text.map_attributes = VisualElementAttributesResolver.resolve_map_attributes(text)
            text.algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(text,
                                                                                           classification=None)
            text.width, text.height = self._algo_display.determine_text_box_dimensions(text)

            city_scatter = [nt for nt in non_texts if isinstance(nt, CityScatter) and nt.city_name == text.city_name][0]

            poly = self._find_best_polygon(
                rtree_map=rtree_map,
                city_scatter=city_scatter,
                text_box=text,
                city_buffer=self._config('algo', 'city_to_text_box_buffer', float),
                number_of_steps=self._config('algo', 'search_steps', float)
            )

            text.polygon = poly

            rtree_map.add_visual_element(text)

        return rtree_map.elements
