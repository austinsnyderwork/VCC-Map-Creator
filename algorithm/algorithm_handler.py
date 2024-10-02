import logging

from . import rtree_analyzer
import config_manager
from algorithm.city_scanning.city_scanner import CityScanner
from .algorithm_plotter import AlgorithmPlotter
from polygons import polygon_factory
from things.visualization_elements import visualization_elements


class AlgorithmHandler:

    def __init__(self, config: config_manager.ConfigManager, polygon_factory_: polygon_factory.PolygonFactory):
        self.config = config
        self.algo_map_plotter = AlgorithmPlotter(
            display_fig_size=(self.config.get_config_value('display.fig_size_x', int), self.config.get_config_value('display.fig_size_y', int)),
            county_line_width=self.config.get_config_value('display.county_line_width', float),
            show_display=self.config.get_config_value('algo_display.show_display', bool))
        self.rtree_analyzer = rtree_analyzer.RtreeAnalyzer()
        self.polygon_factory_ = polygon_factory_

    def plot_element(self, element: visualization_elements.VisualizationElement):
        element_poly_classes = {
            visualization_elements.Line: 'line',
            visualization_elements.CityScatter: 'scatter',
            visualization_elements.CityTextBox: 'text'
        }
        self.algo_map_plotter.plot_element(element)
        self.rtree_analyzer.add_poly(poly_class=element_poly_classes[type(element)],
                                     poly=element.algorithm_poly)

    def find_best_polygon(self, city_element: visualization_elements.CityScatter,
                          text_box_element: visualization_elements.CityTextBox):
        logging.info(f"Finding best poly for {city_element.city_name}")
        city_text_box_search = CityScanner(
            config=self.config,
            text_box=text_box_element.algorithm_box_geometry,
            city_scatter_element=city_element,
            poly_factory=self.polygon_factory_)

        for result in city_text_box_search.find_best_poly(rtree_analyzer_=self.rtree_analyzer):
            yield result
            if type(result.visualization_element) is visualization_elements.Best:
                city_element.best_poly = result.algorithm_poly
        logging.info(f"Found best poly for {city_element.city_name}.")

        self.rtree_analyzer.add_poly(poly=city_element.best_poly,
                                     poly_class='text')
