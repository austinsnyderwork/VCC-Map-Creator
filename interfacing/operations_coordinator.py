import copy
import logging

import matplotlib
import pandas as pd

from config_manager import ConfigManager
from entities.factory import EntitiesFactory, EntitiesContainer
from environment_management.city_origin_networks import CityNetworksHandler
from mapping import MapPlotter
from plotting import NumberOfVisitingProvidersConditionsController, PlotController, PlotManager
from text_box_algorithm.rtree_elements_manager import RtreeElementsManager
from text_box_algorithm.textbox_placement_algorithm import TextboxPlacementAlgorithm
from . import application_manager
from .power_bi_output_formatter import PowerBiOutputFormatter


class OperationsCoordinator:

    def __init__(self, vcc_df: pd.DataFrame):
        self._entities_container = EntitiesFactory.create_entities(vcc_df)
        self._city_networks_handler = CityNetworksHandler().fill_networks(entities_container=self._entities_container)

        config = ConfigManager()
        self.text_box_algorithm = TextboxPlacementAlgorithm(
            rtree_manager=RtreeElementsManager(),
            city_buffer=config('text_box_algorithm.city_to_text_box_buffer', int),
            number_of_search_steps=config('text_box_algorithm.search_steps', int)
        )

        if config('display.show_display', bool):
            self.map_plotter = MapPlotter(
                config_=config,
                display_fig_size=(config('display.fig_size_x', int),
                                  config('display.fig_size_y', int)
                                  ),
                county_line_width=config('display.county_line_width', float)
            )

    def create_map(self, conditions_controller):

    def create_high_volume_line_map(self, number_of_origin_cities: int):


    def create_line_map(self, entities_container: EntitiesContainer = None):
        entities_container = entities_container or self._entities_container

    def create_number_of_visiting_providers_map(self, output_path: str, **kwargs):
        logging.info("Creating number of providers by visiting site mapping.")

        conditions_map = NumberOfVisitingProvidersConditionsController(config=self.config)
        vis_element_plot_controller = PlotController(
            config=self.config,
            show_line=False,
            show_visiting_text_box=False)
        plotter = PlotManager(algorithm_handler=self.algorithm_handler,
                              map_plotter=self.map_plotter,
                              plot_controller=vis_element_plot_controller)

        plotted_elements = self._create_map(conditions_map=conditions_map,
                                            plot_controller=vis_element_plot_controller,
                                            plot_manager=plotter)

        return plotted_elements

        self.pbif.add_visualization_elements(vis_elements)
        df = self.pbif.create_df()
        df.to_csv(output_path)

    def create_highest_volume_line_map(self, output_path: str, results: int):
        vis_elements = self.application_manager.create_highest_volume_line_map(number_of_results=results)
        self.pbif.add_visualization_elements(vis_elements)
        df = self.pbif.create_df()
        df.to_csv(output_path)
