import pandas as pd

from . import data_functions, helper_functions
import algorithm
import config_manager
import environment_management
from environment_management import entity_relationship_manager
from environment_management import CityOriginNetworkHandler
from plotting import plot_configurations
import plotting
from environment_management import entities_factory
import things
from things import visualization_elements
from things import entities
import map


class ApplicationManager:

    def __init__(self, df: pd.DataFrame,
                 entities_factory_: entities_factory.EntitiesFactory = None,
                 map_plotter: map.MapPlotter = None,
                 algorithm_handler: algorithm.AlgorithmHandler = None):
        self.df = df
        self.config = config_manager.ConfigManager()
        self.entities_manager = entities.EntitiesManager()
        self.city_origin_network_handler = CityOriginNetworkHandler(colors=helper_functions.get_colors())
        self.entities_factory_ = entities_factory_ if entities_factory_ \
            else entities_factory.EntitiesFactory(df=self.df)

        self.map_plotter = map_plotter or map.MapPlotter(
            config_=self.config,
            display_fig_size=(self.config.get_config_value('display.fig_size_x', int), self.config.get_config_value('display.fig_size_y', int)),
            county_line_width=self.config.get_config_value('display.county_line_width', float),
            show_display=self.config.get_config_value('map_display.show_display', bool)
        )
        self.vis_elements_manager = visualization_elements.VisualizationElementsManager()

        self.algorithm_handler = algorithm_handler or algorithm.AlgorithmHandler(config=self.config)
        self.thing_converter = things.thing_converter.ThingConverter(
            config=self.config,
            entities_manager=self.entities_manager,
            city_origin_network_handler=self.city_origin_network_handler,
            get_text_display_dimensions=self.map_plotter.get_text_box_dimensions)

    def startup(self):
        entities_ = self.entities_factory_.create_entities(coord_converter=self.map_plotter.convert_coord_to_display)
        all_entities = [entity for entities_list in entities_.values() for entity in entities_list]

        for entity in all_entities:
            self.entities_manager.add_entity(entity)

        entity_relationship_manager_ = entity_relationship_manager.EntityRelationshipManager(
            cities=entities_[entities.City],
            clinics=entities_[entities.VccClinicSite],
            provider_assignments=entities_[entities.ProviderAssignment]
        )
        entity_relationship_manager_.fill_entities()
        self.city_origin_network_handler.fill_city_origin_networks(entities_manager=self.entities_manager)

    def create_line_map(self):
        entity_plot_controller = environment_management.VisualizationElementPlotController()

    def create_highest_volume_line_map(self, number_of_results: int):
        highest_volume_cities = data_functions.get_top_volume_incoming_cities(df=self.df,
                                                                              num_results=number_of_results)
        conditions_map = plot_configurations.HighestCityVisitingVolumeConditions(
            highest_volume_cities=highest_volume_cities,
            config=self.config)
        vis_element_plot_controller = plot_configurations.PlotController(
            config=self.config,
            show_visiting_text_boxes=False)
        visualization_elements =
        intial_entities = self.entities_manager.get_all_entities(entities_type=[entities.City, entities.ProviderAssignment])
        vis_elements = []
        for entity in intial_entities:
            if type(entity) in conditions_map.visualization_elements_types:
                vis_element = conditions_map.get_visualization_element_for_condition(entity)
            else:
                vis_element = self.thing_converter.convert_thing(entity)
            vis_elements.append(vis_element)
        plot = plotting.PlotManager(entities_manager=self.entities_manager,
                                    plot_controller=vis_element_plot_controller,
                                    conditions_map=conditions_map,
                                    thing_converter=self.thing_converter,
                                    algorithm_plotter=self.algorithm_handler.algo_map_plotter,
                                    map_plotter=self.map_plotter)
        plot.plot()

    def create_number_of_visiting_providers_map(self):
        conditions_map = plot_configurations.NumberOfVisitingProvidersConditions()
        vis_element_plot_controller = plot_configurations.PlotController(
            entity_conditions_map=conditions_map,
            should_plot_origin_lines=False,
            should_plot_outpatient_lines=False,
            should_plot_origin_text_box=False
        )
        city_objs = list(self.entitites_manager.get.cities_directory.values())
        for iteration, city_obj in enumerate(city_objs):
            conditions_map.get_visualization_element_for_condition(num_visiting_providers=len(city_obj.visiting_providers))
            if vis_element_plot_controller.should_display(entity_type=entities.City,
                                                          iterations=iteration,
                                                          display_type='algorithm'):
                self.algorithm_handler.plot_point()
        """
        For every city in environment entities, plot that city scatter if it is one of the highest volume cities.
        Then, plot a text box for every city."""


