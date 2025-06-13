import pandas as pd
from matplotlib import pyplot as plt
from mpl_toolkits.basemap import Basemap

import plotting
from config_manager import ConfigManager
from entities.factory import EntitiesFactory
from environment_management.city_origin_networks import CityNetworksHandler
from plot_maps.base_classes import ConditionsController
from plotting import AlgorithmDisplay
from polygons.polygon_factory import PolygonFactory
from text_box_algorithm.rtree_elements_manager import RtreeVisualElementsMap
from text_box_algorithm.textbox_placement_algorithm import TextboxPlacementAlgorithm
from visual_elements.attributes_resolver import VisualElementAttributesResolver
from visual_elements.element_classes import TextBox, CityScatter, Line, AlgorithmClassification


def _create_iowa_basemap(figsize):

    fig, ax = plt.subplots(figsize=figsize)

    # Create Basemap instance with Lambert Conformal Conic projection for the region around Iowa
    m = Basemap(
        projection='lcc',
        resolution='i',
        lat_0=42.0,
        lon_0=-93.5,
        width=700000,
        height=500000,
        ax=ax
    )

    x_min, y_min = m(-97, 40)  # lower-left corner in lon/lat
    x_max, y_max = m(-90, 44)  # upper-right corner in lon/lat

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Draw coastlines, countries, states
    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.drawcounties()

    fig.canvas.draw()

    return fig, ax, m


class OperationsCoordinator:

    def __init__(self,
                 vcc_df: pd.DataFrame,
                 city_name_changes: dict):
        print("Building EntitiesContainer.")
        self._config = ConfigManager()
        fig, ax, m = _create_iowa_basemap(
            (
                self._config('algo.display', 'fig_size_x', int),
                self._config('algo.display', 'fig_size_y', int)
            )
        )
        self._entities_container = EntitiesFactory.create_entities(vcc_df, projection=m)

        print("Building CityNetworksHandler.")
        self._city_networks_handler = CityNetworksHandler().fill_networks(entities_container=self._entities_container)

        self._show_algo = self._config('algo.display', 'show_display', bool)
        self._algo_display = AlgorithmDisplay(
            fig=fig,
            ax=ax,
            show_pause=self._config('algo.display', 'show_pause', float),
            display_zoom_out=self._config('algo.display', 'display_zoom_out', int),
            show_display=self._show_algo
        )

    def create_map(self, controller_class: type(ConditionsController)):
        print("Creating map.")

        conditions_controller = controller_class(
            entities_container=self._entities_container,
            city_networks_handler=self._city_networks_handler
        )

        print("Initializing Rtree and TextboxPlacementAlgorithm.")
        rtree_map = RtreeVisualElementsMap()
        text_box_algorithm = TextboxPlacementAlgorithm(
            number_of_search_steps=self._config('algo', 'search_steps', int),
            rtree_map=rtree_map
        )

        print("Determining VisualElements for each Entity.")
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
                """print(f"Creating Line polygon.\n\tCoord0: {non_text.origin_coordinate}\n\t"
                      f"Coord1: {non_text.visiting_coordinate}\n\tWidth: {non_text.algo_attributes.linewidth}")"""
                line_poly = PolygonFactory.create_line(
                    coord_0=non_text.origin_coordinate,
                    coord_1=non_text.visiting_coordinate,
                    width=non_text.linewidth
                )
                non_text.polygon = line_poly
                rtree_map.add_visual_element(visual_element=non_text)

                if self._show_algo:
                    self._algo_display.plot_element(non_text,
                                                    show_display=False,
                                                    classification=AlgorithmClassification.LINE)

            elif isinstance(non_text, CityScatter):
                # print(f"Creating CityScatter polygon.\n\tCoord: {non_text.coord}\n\tRadius: {non_text.radius}")
                scatter_poly = PolygonFactory.create_scatter(
                    coord=non_text.coord,
                    radius=non_text.radius
                )
                non_text.polygon = scatter_poly
                rtree_map.add_visual_element(visual_element=non_text)

                if self._show_algo:
                    self._algo_display.plot_element(non_text,
                                                    show_display=False,
                                                    classification=AlgorithmClassification.CITY_SCATTER)

        # 3. Use the non-TextBox visual elements in the RTree to determine the best placement for TextBoxes
        for text in texts:
            text.width, text.height = self._algo_display.determine_text_box_dimensions(
                text,
                fontsize=text.fontsize,
                fontweight=text.fontweight
            )

            city_scatter = [nt for nt in non_texts if isinstance(nt, CityScatter) and nt.city_name == text.city_name][0]

            """if self._show_algo:
                self._algo_display.center_display(city_scatter)"""

            print(f"Finding best poly for city '{city_scatter.city_name}'")

            for elements, classification in text_box_algorithm.find_best_poly(
                    text_box=text,
                    city_scatter=city_scatter
            ):
                if classification == AlgorithmClassification.TEXT_BEST:
                    best = elements[0]

                    text.polygon = best.polygon
                    text.centroid_coord = best.centroid_coord

                    print(f"Rtree inserting Best for {text.city_name}")
                    rtree_map.add_visual_element(text)

                if self._show_algo:
                    # print(f"Algorithm plotting {len(elements)}: {classification}")
                    for element in elements:
                        self._algo_display.plot_element(visual_element=element,
                                                        classification=classification,
                                                        show_display=self._show_algo)

        if self._show_algo:
            self._algo_display.fig.canvas.draw()

        return rtree_map.elements
