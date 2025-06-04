import logging

from things import box_geometry

import config_manager
from polygons import polygon_factory
from polygons.polygon_factory import PolygonFactory
from visualization_elements.element_classes import TextBoxClassification
from .plotter import AlgorithmPlotter
from .textbox_placement_algorithm import TextboxPlacementAlgorithm


class AlgorithmHandler:

    def __init__(self, config: config_manager.ConfigManager, polygon_factory_: polygon_factory.PolygonFactory):
        self._config = config
        
        self._plot_algorithm = self._config('algo_display.show_display', bool)
        if self._plot_algorithm:
            self._algorithm_plotter = AlgorithmPlotter(
                config=config,
                display_fig_size=(self._config('display.fig_size_x', int), self._config('display.fig_size_y', int)),
                county_line_width=self._config('display.county_line_width', float),
                show_display=self._config('algo_display.show_display', bool),
                show_pause=self._config('algo_display.show_pause', float))
        else:
            self._algorithm_plotter = None

        self._rtree_analyzer = rtree_analyzer.RtreeElementsManager()
        self._polygon_factory_ = polygon_factory_

    def find_best_polygon(self,
                          city_scatter: CityScatter,
                          text_box: TextBox,
                          city_buffer: int,
                          number_of_steps: int):
        logging.info(f"Finding best poly for city '{city_scatter.city_name}'")
        text_box = box_geometry.BoxGeometry(**text_box.bounds)

        algo = TextboxPlacementAlgorithm(
            config=self._config,
            rtree_manager=self._rtree_analyzer,
            city_buffer=city_buffer,
            number_of_search_steps=number_of_steps
        )
        for elements, classification in algo.find_best_poly(text_box=text_box,
                                                            city_scatter=city_scatter):
            if self._plot_algorithm:
                for element in elements:
                    self._algorithm_plotter.plot_element(element=element,
                                                        classification=classification)

            if classification == TextBoxClassification.BEST:
                best = elements[0]
                self._rtree_analyzer.add_visualization_element(best)
                
                logging.info(f"Found best poly for {city_scatter.city_name}.")
                
                return PolygonFactory.create_rectangle(**best.bounds)

