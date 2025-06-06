import logging

from shapely import Polygon

from config_manager import ConfigManager
from polygons.polygon_factory import PolygonFactory
from visual_elements.element_classes import TextBoxClassification, CityScatter, TextBox
from plotting import AlgorithmDisplay
from .rtree_elements_manager import RtreeVisualElementsMap
from .textbox_placement_algorithm import TextboxPlacementAlgorithm


class AlgorithmHandler:

    def __init__(self, config: ConfigManager):
        self._config = config
        
        self._plot_algorithm = self._config('algo.display', 'show_display', bool)

        self._algo_display = AlgorithmDisplay(
            figure_size=(
                self._config('algo.display', 'fig_size_x', int),
                self._config('algo.display', 'fig_size_y', int)
            ),
            county_line_width=self._config('algo.display', 'county_line_width', float),
            show_pause=self._config('algo.display', 'show_pause', float)
        ) if config('algo.display', 'show_display', bool) else None

        self._rtree_visual_elements_map = RtreeVisualElementsMap()

    def find_best_polygon(self,
                          city_scatter: CityScatter,
                          text_box: TextBox,
                          city_buffer: int,
                          number_of_steps: int) -> Polygon:
        logging.info(f"Finding best poly for city '{city_scatter.city_name}'")

        algo = TextboxPlacementAlgorithm(
            rtree_map=self._rtree_visual_elements_map,
            city_buffer=city_buffer,
            number_of_search_steps=number_of_steps
        )
        for element, classification in algo.find_best_poly(text_box=text_box,
                                                           city_scatter=city_scatter):
            if self._plot_algorithm:
                self._algo_display.plot_element(visual_element=element,
                                                classification=classification,
                                                center_view=True)
                self._algo_display.show_display()

            if classification == TextBoxClassification.BEST:
                logging.info(f"Found best poly for {city_scatter.city_name}.")
                
                return PolygonFactory.create_rectangle(**element.bounds)

