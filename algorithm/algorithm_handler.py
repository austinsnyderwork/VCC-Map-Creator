import logging

from . import rtree_analyzer
import config_manager
from algorithm.city_scanning.city_scanner import CityScanner
from .algorithm_plotter import AlgorithmPlotter
from polygons import polygon_factory
from things import box_geometry
from things.visualization_elements import visualization_elements


class AlgorithmHandler:

    def __init__(self, config: config_manager.ConfigManager, polygon_factory_: polygon_factory.PolygonFactory):
        self.config = config
        self.algorithm_plotter = AlgorithmPlotter(
            display_fig_size=(self.config.get_config_value('display.fig_size_x', int), self.config.get_config_value('display.fig_size_y', int)),
            county_line_width=self.config.get_config_value('display.county_line_width', float),
            show_display=self.config.get_config_value('algo_display.show_display', bool),
            show_pause=self.config.get_config_value('algo_display.show_pause', float))
        self.rtree_analyzer_ = rtree_analyzer.RtreeAnalyzer()
        self.polygon_factory_ = polygon_factory_

    def plot_element(self, element: visualization_elements.VisualizationElement):
        self.algorithm_plotter.plot_element(element)

    def add_element_to_algorithm(self, element: visualization_elements.VisualizationElement):
        self.rtree_analyzer_.add_visualization_element(visualization_element=element,
                                                       poly=element.poly)

    def find_best_polygon(self, city_element: visualization_elements.CityScatter,
                          text_box_element: visualization_elements.CityTextBox, city_buffer: int, number_of_steps: int):
        logging.info(f"Finding best poly for {city_element.city_name}")
        text_box = box_geometry.BoxGeometry(dimensions={
                'x_min': text_box_element.x_min,
                'y_min': text_box_element.y_min,
                'x_max': text_box_element.x_max,
                'y_max': text_box_element.y_max
            })
        city_text_box_search = CityScanner(
            config=self.config,
            text_box=text_box,
            city_scatter_element=city_element,
            poly_factory=self.polygon_factory_,
            city_buffer=city_buffer,
            number_of_search_steps=number_of_steps)

        for vis_element in city_text_box_search.find_best_poly(rtree_analyzer_=self.rtree_analyzer_):
            yield vis_element
            if type(vis_element) is visualization_elements.Best:
                best = vis_element
        logging.info(f"Found best poly for {city_element.city_name}.")

        self.add_element_to_algorithm(element=best)
        self.plot_element(element=best)
