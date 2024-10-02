import logging
import matplotlib.pyplot as plt
import pandas as pd
from typing import Union

from . import data_functions, helper_functions
import algorithm
import config_manager
import environment_management
from environment_management import entity_relationship_manager
from environment_management import CityOriginNetworkHandler
import plotting
from polygons import polygon_factory
import things
from things import visualization_elements, entities_factory
from things import entities
import map


def _remove_same_city_visiting_assignments(entities_: list[entities.Entity]) -> set[entities.Entity]:
    correct_entities = set()
    for entity in entities_:
        if type(entity) is entities.ProviderAssignment and entity.origin_city_name == entity.visiting_city_name:
            continue
        correct_entities.add(entity)
    return correct_entities


class ApplicationManager:

    def __init__(self, df: pd.DataFrame,
                 entities_factory_: entities_factory.EntitiesFactory = None,
                 map_plotter: map.MapPlotter = None,
                 algorithm_handler: algorithm.AlgorithmHandler = None):
        self.df = df
        self.config = config_manager.ConfigManager()
        self.entities_manager = entities.EntitiesManager()
        self.visualization_elements_manager = visualization_elements.VisualizationElementsManager()
        self.polygon_factory_ = polygon_factory.PolygonFactory(
            radius_per_scatter_size=self.config.get_config_value('dimensions.units_radius_per_1_scatter_size', int),
            units_per_line_width=self.config.get_config_value('dimensions.units_per_1_linewidth', int)
        )
        self.city_origin_network_handler = CityOriginNetworkHandler(colors=helper_functions.get_colors())
        self.entities_factory_ = entities_factory_ if entities_factory_ \
            else entities_factory.EntitiesFactory(df=self.df)

        self.map_plotter = map_plotter or map.MapPlotter(
            config_=self.config,
            display_fig_size=(self.config.get_config_value('display.fig_size_x', int),
                              self.config.get_config_value('display.fig_size_y', int)),
            county_line_width=self.config.get_config_value('display.county_line_width', float),
            show_display=self.config.get_config_value('map_display.show_display', bool)
        )

        self.algorithm_handler = algorithm_handler or algorithm.AlgorithmHandler(config=self.config,
                                                                                 polygon_factory_=self.polygon_factory_)
        self.thing_converter = things.thing_converter.ThingConverter(
            config=self.config,
            entities_manager=self.entities_manager,
            city_origin_network_handler=self.city_origin_network_handler,
            get_text_display_dimensions=self.map_plotter.get_text_box_dimensions)

    def startup(self):
        logging.info("Beginning startup.")
        entities_ = self.entities_factory_.create_entities(coord_converter=self.map_plotter.convert_coord_to_display)
        all_entities = [entity for entities_list in entities_.values() for entity in entities_list]

        for entity in all_entities:
            logging.debug(f"Attempting to add entity {entity} to entities_manager")
            self.entities_manager.add_entity(entity)

        entity_relationship_manager_ = entity_relationship_manager.EntityRelationshipManager(
            cities=entities_[entities.City],
            clinics=entities_[entities.VccClinicSite],
            provider_assignments=entities_[entities.ProviderAssignment]
        )
        entity_relationship_manager_.fill_entities()
        self.city_origin_network_handler.fill_city_origin_networks(entities_manager=self.entities_manager)
        logging.info("Finished startup.")

    def _convert_entity_to_vis_elements(self, entity: entities.Entity, conditions_map) \
            -> Union[list[visualization_elements.VisualizationElement], None]:
        conditional_vis_element = None
        if type(entity) in conditions_map.entity_types:
            conditional_vis_element = conditions_map.get_visualization_element_for_condition(entity=entity,
                                                                                             **entity.__dict__)
            if not conditional_vis_element:
                return

        vis_elements = conditional_vis_element if conditional_vis_element else self.thing_converter.convert_thing(
            entity)

        for vis_element in vis_elements:
            self.thing_converter.fill_in_data(entity=entity, visualization_element=vis_element)

        vis_elements = [vis_elements] if not isinstance(vis_elements, list) else vis_elements
        return vis_elements

    def _convert_entities_to_vis_elements(self, entities_: list[entities.Entity], conditions_map):
        vis_elements = []
        for i, entity in enumerate(entities_):
            logging.info(f"Converting entity number {i} of {len(entities_)}.\n\tEntity type: {str(type(entity))}")
            if type(entity) is entities.ProviderAssignment:
                logging.info(f"Origin city: {entity.origin_city_name}, Visiting city: {entity.visiting_city_name}")
            new_vis_elements = self._convert_entity_to_vis_elements(entity, conditions_map=conditions_map)
            # convert_entity returns None when the entity is valid for the conditions map, but doesn't meet any of the
            # conditions
            if not new_vis_elements:
                continue
            vis_elements.extend(new_vis_elements)
        return vis_elements

    def _fill_visualization_elements_with_polygons(self, plotter: plotting.PlotManager,
                                                   visualization_elements_: list[visualization_elements.VisualizationElement]):
        for i, visualization_element in enumerate(visualization_elements_):
            logging.info(f"\tFilling visualization element {visualization_element} "
                         f"\n\t\tNumber {i} of {len(visualization_elements_)}")
            extra_args = plotter.get_text_box_bounds(visualization_element) \
                if (type(visualization_element) is visualization_elements.CityTextBox) else visualization_element.__dict__
            poly = self.polygon_factory_.create_poly(vis_element=visualization_element,
                                                     **extra_args)

            if issubclass(type(visualization_element), visualization_elements.DualVisualizationElement):
                visualization_element.algorithm_poly = poly
            else:
                visualization_element.poly = poly

    def _create_entities(self, entities_types: list, filter_same_city_visiting_assignments: bool = False):
        entities_ = self.entities_manager.get_all_entities(entities_types)
        if filter_same_city_visiting_assignments:
            entities_ = _remove_same_city_visiting_assignments(entities_=entities_)
        return entities_

    def create_highest_volume_line_map(self, number_of_results: int):
        logging.info("Creating highest volume line map.")
        highest_volume_cities = data_functions.get_top_volume_incoming_cities(df=self.df,
                                                                              num_results=number_of_results)
        conditions_map = plotting.HighestCityVisitingVolumeConditions(
            highest_volume_cities=highest_volume_cities,
            config=self.config)
        vis_element_plot_controller = plotting.PlotController(
            config=self.config,
            show_visiting_text_boxes=False)
        plotter = plotting.PlotManager(algorithm_handler=self.algorithm_handler,
                                       map_plotter=self.map_plotter,
                                       plot_controller=vis_element_plot_controller)

        entities_ = self._create_entities(entities_types=[entities.City, entities.ProviderAssignment],
                                          filter_same_city_visiting_assignments=True)
        vis_elements = self._convert_entities_to_vis_elements(entities_=entities_,
                                                              conditions_map=conditions_map)
        self._fill_visualization_elements_with_polygons(visualization_elements_=vis_elements,
                                                        plotter=plotter)
        self.visualization_elements_manager.add_visualization_elements(vis_elements)

        non_text_vis_elements = self.visualization_elements_manager.get_all([visualization_elements.CityScatter,
                                                                             visualization_elements.Line])
        for vis_element in non_text_vis_elements:
            plotter.attempt_plot(display_types=['algorithm'],
                                 vis_element=vis_element)

        # Now we search for the best coordinate for each CityTextBox visualization element
        for city_scatter_and_text in self.visualization_elements_manager.city_scatter_and_texts:
            for vis_element in self.algorithm_handler.find_best_polygon(city_element=city_scatter_and_text.city_scatter,
                                                                        text_box_element=city_scatter_and_text.city_text_box):
                plotter.attempt_plot(vis_element=vis_element)


