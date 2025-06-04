import logging
from typing import Union

import pandas as pd

import config_manager
import entities
from mapping import MapPlotter
import plotting
from environment_management import CityOriginNetworkHandler
from environment_management import entity_relationship_manager
from plotting import VisualizationElementResult
from text_box_algorithm.rtree_elements_manager import RtreeElementsManager
from text_box_algorithm.textbox_placement_algorithm import TextboxPlacementAlgorithm
from . import data_functions, helper_functions
from entities.factory import EntitiesFactory
from text_box_algorithm


class ApplicationManager:

    def __init__(self,
                 df: pd.DataFrame,
                 map_plotter: map.MapPlotter = None):
        self.df = df
        self.config = config_manager.ConfigManager()

        self.entities_container = EntitiesFactory.create_entities(df=df)
        self.rtree_manager = RtreeElementsManager()

        if self.config('display.show_display'):
            self.map_plotter = map_plotter or MapPlotter(
                config_=self.config,
                display_fig_size=(self.config.get_config_value('display.fig_size_x', int),
                                  self.config.get_config_value('display.fig_size_y', int)),
                county_line_width=self.config.get_config_value('display.county_line_width', float)
            )

    def create_highest_volume_line_map(self, number_of_results: int):
        logging.info("Creating highest volume line mapping.")

        highest_volume_cities = data_functions.get_top_volume_origin_cities(df=self.df,
                                                                            num_results=number_of_results)

        provider_assignments = self.entities_container.provider_assignments
        visiting_from_high_vol_city = set(
            assignment.visiting_city_name for assignment in provider_assignments
            if assignment.origin_city_name in highest_volume_cities
        )
        all_plot_cities = set(highest_volume_cities) | visiting_from_high_vol_city
        conditions_map = plotting.HighestOriginVolumeController(
            origin_cities=highest_volume_cities,
            all_plot_cities=all_plot_cities,
            config=self.config
        )
        vis_element_plot_controller = plotting.PlotController(
            config=self.config,
            show_visiting_text_boxes=False
        )
        plotter = plotting.PlotManager(algorithm_handler=self.algorithm_handler,
                                       map_plotter=self.map_plotter,
                                       plot_controller=vis_element_plot_controller)

        plotted_elements = self._create_map(conditions_map=conditions_map,
                                            plot_controller=vis_element_plot_controller,
                                            plot_manager=plotter)

        return plotted_elements

    def create_number_of_visiting_providers_map(self):
        logging.info("Creating number of providers by visiting site mapping.")

        conditions_map = plotting.NumberOfVisitingProvidersConditionsController(config=self.config)
        vis_element_plot_controller = plotting.PlotController(
            config=self.config,
            show_line=False,
            show_visiting_text_box=False)
        plotter = plotting.PlotManager(algorithm_handler=self.algorithm_handler,
                                       map_plotter=self.map_plotter,
                                       plot_controller=vis_element_plot_controller)

        plotted_elements = self._create_map(conditions_map=conditions_map,
                                            plot_controller=vis_element_plot_controller,
                                            plot_manager=plotter)

        return plotted_elements
