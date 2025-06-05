import logging

from shared.shared_utils import BoxGeometry
from visual_elements.element_classes import TextBoxClassification, CityScatter, TextBox

from config_manager import ConfigManager
from polygons.polygon_factory import PolygonFactory
from .plotter import AlgorithmDisplay
from .rtree_elements_manager import RtreeVisualElementsMap
from .textbox_placement_algorithm import TextboxPlacementAlgorithm


class AlgorithmHandler:

    def __init__(self, config: ConfigManager):
        self._config = config
        
        self._plot_algorithm = self._config('algo_display.show_display', bool)

        self._algo_display = AlgorithmDisplay(
            display_fig_size=(self._config('display.fig_size_x', int), self._config('display.fig_size_y', int)),
            county_line_width=self._config('display.county_line_width', float),
            show_pause=self._config('algo_display.show_pause', float)
        ) if config('algo_display.show_display', bool) else None

        self._rtree_visual_elements_map = RtreeVisualElementsMap()

    def find_best_polygon(self,
                          city_scatter: CityScatter,
                          text_box: TextBox,
                          city_buffer: int,
                          number_of_steps: int):
        logging.info(f"Finding best poly for city '{city_scatter.city_name}'")

        algo = TextboxPlacementAlgorithm(
            rtree_map=self._rtree_visual_elements_map,
            city_buffer=city_buffer,
            number_of_search_steps=number_of_steps
        )
        for elements, classification in algo.find_best_poly(text_box=text_box,
                                                            city_scatter=city_scatter):
            if self._plot_algorithm:
                for element in elements:
                    self._algo_display.display_element(element=element,
                                                       classification=classification)

            if classification == TextBoxClassification.BEST:
                best = elements[0]
                
                logging.info(f"Found best poly for {city_scatter.city_name}.")
                
                return PolygonFactory.create_rectangle(**best.bounds)

