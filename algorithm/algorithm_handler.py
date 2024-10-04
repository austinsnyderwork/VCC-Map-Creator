import copy
import logging

from . import rtree_analyzer
import config_manager
from algorithm.city_scanning import CityScanner
from .algorithm_plotter import AlgorithmPlotter
from polygons import polygon_functions, polygon_factory
from things import box_geometry, thing_converter
from things.visualization_elements import vis_element_classes


class AlgorithmHandler:

    def __init__(self, config: config_manager.ConfigManager, polygon_factory_: polygon_factory.PolygonFactory):
        self.config = config
        self.algorithm_plotter = AlgorithmPlotter(
            config=config,
            display_fig_size=(self.config.get_config_value('display.fig_size_x', int), self.config.get_config_value('display.fig_size_y', int)),
            county_line_width=self.config.get_config_value('display.county_line_width', float),
            show_display=self.config.get_config_value('algo_display.show_display', bool),
            show_pause=self.config.get_config_value('algo_display.show_pause', float))
        self.rtree_analyzer_ = rtree_analyzer.RtreeAnalyzer()
        self.polygon_factory_ = polygon_factory_

    def plot_element(self, element: vis_element_classes.VisualizationElement):
        new_poly = None
        # Shorten the line for the algorithm
        if type(element) is vis_element_classes.Line:
            new_x_data, new_y_data = polygon_functions.shorten_line(element.x_data, element.y_data)
            new_poly = self.polygon_factory_.create_poly(vis_element_type=vis_element_classes.Line,
                                                         x_data=new_x_data,
                                                         y_data=new_y_data,
                                                         linewidth=element.map_linewidth)
        self.algorithm_plotter.plot_element(element, poly_override=new_poly)

    def add_element_to_algorithm(self, element: vis_element_classes.VisualizationElement, poly_override=None):
        poly = poly_override if poly_override else element.default_poly
        self.rtree_analyzer_.add_visualization_element(visualization_element=element,
                                                       poly=poly)

    def find_best_polygon(self, city_element: vis_element_classes.CityScatter,
                          text_box_element: vis_element_classes.CityTextBox, city_buffer: int, number_of_steps: int):
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

        for vis_element_result in city_text_box_search.find_best_poly(rtree_analyzer_=self.rtree_analyzer_):
            yield vis_element_result
            if type(vis_element_result.vis_element) is vis_element_classes.Best:
                best_vis_element = vis_element_result.vis_element
                centroid = best_vis_element.default_poly.centroid
                thing_converter.convert_visualization_element(vis_element=text_box_element,
                                                              new_vis_element=best_vis_element,
                                                              city_name=city_element.city_name,
                                                              poly_coord=(centroid.x, centroid.y))
        logging.info(f"Found best poly for {city_element.city_name}.")

        self.add_element_to_algorithm(element=best_vis_element)
        self.plot_element(element=best_vis_element)
