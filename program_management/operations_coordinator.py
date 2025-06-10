import pandas as pd
from shapely import Polygon

from config_manager import ConfigManager
from entities.factory import EntitiesFactory
from environment_management.city_origin_networks import CityNetworksHandler
from plotting import MapDisplay, AlgorithmDisplay
from plot_maps.base_classes import ConditionsController
from plotting.visual_attributes_resolver import VisualElementAttributesResolver
from polygons.polygon_factory import PolygonFactory
from text_box_algorithm.rtree_elements_manager import RtreeVisualElementsMap
from text_box_algorithm.textbox_placement_algorithm import TextboxPlacementAlgorithm
from visual_elements.element_classes import TextBox, CityScatter, Line, TextBoxClassification
from .crs_conversion import convert_crs


class OperationsCoordinator:

    def __init__(self, vcc_df: pd.DataFrame):
        vcc_df = convert_crs(vcc_df)

        print("Building EntitiesContainer.")
        self._entities_container = EntitiesFactory.create_entities(vcc_df)

        print("Building CityNetworksHandler.")
        self._city_networks_handler = CityNetworksHandler().fill_networks(entities_container=self._entities_container)

        self._config = ConfigManager()
        self.text_box_algorithm = TextboxPlacementAlgorithm(
            rtree_map=RtreeVisualElementsMap(),
            city_buffer=self._config('algo', 'city_to_text_box_buffer', float),
            number_of_search_steps=self._config('algo', 'search_steps', int)
        )

        self._map_display = MapDisplay(
            figure_size=(
                self._config('map.display', 'fig_size_x', float),
                self._config('map.display', 'fig_size_y', float)
            ),
            county_line_width=self._config('map.display', 'county_line_width', float)
        )

        self._algo_display = None
        if self._config('algo.display', 'show_display', bool):
            self._algo_display = AlgorithmDisplay(
                figure_size=(
                    self._config('algo.display', 'fig_size_x', int),
                    self._config('algo.display', 'fig_size_y', int)
                ),
                county_line_width=self._config('algo.display', 'county_line_width', float),
                show_pause=self._config('algo.display', 'show_pause', float)
            )

        self._rtree_visual_elements_map = RtreeVisualElementsMap()

    def _find_best_polygon(self,
                           city_scatter: CityScatter,
                           text_box: TextBox,
                           city_buffer: int,
                           number_of_steps: int) -> Polygon:
        print(f"Finding best poly for city '{city_scatter.city_name}'")

        # Center on the scan area
        self._algo_display.center_display(visual_element=city_scatter)

        algo = TextboxPlacementAlgorithm(
            rtree_map=self._rtree_visual_elements_map,
            city_buffer=city_buffer,
            number_of_search_steps=number_of_steps
        )
        for elements, classification in algo.find_best_poly(text_box=text_box,
                                                            city_scatter=city_scatter):
            if self._algo_display:
                print(f"Algorithm plotting {len(elements)}: {classification}")
                for element in elements:
                    self._algo_display.plot_element(visual_element=element,
                                                    classification=classification)
                    self._algo_display.show_display()

                    if classification == TextBoxClassification.BEST:
                        print(f"Rtree inserting Best for {text_box.city_name}")
                        self._rtree_visual_elements_map.add_visual_element(element)

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
            for ve in conditions_controller.determine_visual_element(entity)
        ]
        texts = [element for element in elements if isinstance(element, TextBox)]
        non_texts = [element for element in elements if not isinstance(element, TextBox)]

        print(f"ConditionsController returned {len(elements)} total elements. {len(texts)} texts and {len(non_texts)} non-texts.")

        # 2. Create a polygon for each non-TextBox entity (TextBoxes need their centroid determined by the
        # TextBoxPlacementAlgorithm). Then add the VisualElement with its new polygon into the RtreeVisualElementMap
        for non_text in non_texts:
            if isinstance(non_text, Line):
                line_poly = PolygonFactory.create_line(
                    coord_0=non_text.origin_coordinate,
                    coord_1=non_text.visiting_coordinate,
                    width=non_text.algo_attributes['linewidth']
                )
                non_text.polygon = line_poly
            elif isinstance(non_text, CityScatter):
                scatter_poly = PolygonFactory.create_scatter(
                    coord=non_text.coord,
                    radius=non_text.radius
                )
                non_text.polygon = scatter_poly

            self._map_display.plot_element(non_text)
            rtree_map.add_visual_element(visual_element=non_text)

        for non_text in non_texts:
            self._rtree_visual_elements_map.add_visual_element(non_text)
            self._algo_display.plot_element(non_text)

        # 3. Use the non-TextBox visual elements in the RTree to determine the best placement for TextBoxes
        for text in texts:
            text_box_width, text_box_height = self._map_display.determine_text_box_dimensions(text_box=text)

            text.width = text_box_width
            text.height = text_box_height

            city_scatter = [nt for nt in non_texts if isinstance(nt, CityScatter) and nt.city_name == text.city_name][0]

            poly = self._find_best_polygon(
                city_scatter=city_scatter,
                text_box=text,
                city_buffer=self._config('algo', 'city_to_text_box_buffer', float),
                number_of_steps=self._config('algo', 'search_steps', float)
            )

            text.polygon = poly

            rtree_map.add_visual_element(text)

            self._map_display.plot_element(text)
