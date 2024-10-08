import logging
import pandas as pd
from typing import Union

from . import data_functions, helper_functions
import algorithm
import config_manager
from environment_management import entity_relationship_manager
from environment_management import CityOriginNetworkHandler
import plotting
from plotting import VisualizationElementResult
from polygons import polygon_factory
import things
from things import visualization_elements
from things.visualization_elements import CityScatter, Best, Line
from things.entities import entities_factory
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
        self.visualization_elements_manager = visualization_elements.VisualizationElementsManager(config=self.config)
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

        self.entities_ = []

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

    def get_powerbi_output(self):
        vis_elements = self.algorithm_handler.plotted_vis_elements
        all_column_names = {vis_element_type: set() for vis_element_type in vis_elements.keys()}
        for vis_element_type, typed_elements in vis_elements.items():
            col_names = set()
            for ele in typed_elements:
                new_cols = set(ele.__dict__.keys())
                col_names.update(new_cols)
            all_column_names[vis_element_type].update(col_names)

    def _convert_entity(self, entity: entities.Entity, conditions_map) \
            -> Union[visualization_elements.Line, visualization_elements.CityScatterAndText, None]:
        conditional_vis_element = None
        if type(entity) in conditions_map.entity_types:
            conditional_vis_element = conditions_map.get_visualization_element_for_condition(entity=entity,
                                                                                             **entity.__dict__)
            if not conditional_vis_element:
                return

        vis_element = conditional_vis_element if conditional_vis_element else self.thing_converter.convert_thing(entity)

        if type(vis_element) is visualization_elements.CityScatterAndText:
            self.thing_converter.fill_in_data(entity=entity, visualization_element=vis_element.city_scatter)
            self.thing_converter.fill_in_data(entity=entity, visualization_element=vis_element.city_text_box)
            vis_element.city_name = vis_element.city_scatter.city_name
        else:
            self.thing_converter.fill_in_data(entity=entity, visualization_element=vis_element)

        return vis_element

    def _convert_entities_to_vis_elements(self, entities_: list[entities.Entity], plot_controller, conditions_map) \
            -> list[visualization_elements.VisualizationElement]:
        vis_elements = []
        for i, entity in enumerate(entities_):
            logging.info(f"Converting entity number {i} of {len(entities_)}.\n\tEntity type: {str(type(entity))}")
            new_vis_element = self._convert_entity(entity, conditions_map=conditions_map)

            # convert_entity returns None when the entity is valid for the conditions map, but doesn't meet any of the
            # conditions
            if not new_vis_element:
                continue

            if type(new_vis_element) is visualization_elements.CityScatterAndText:
                if plot_controller.should_display(new_vis_element.city_scatter, display_type='map'):
                    vis_elements.append(new_vis_element.city_scatter)
                else:
                    continue
                if plot_controller.should_display(new_vis_element.city_text_box, display_type='map'):
                    vis_elements.append(new_vis_element.city_text_box)
                else:
                    continue
                # We only add this CityScatterAndText if we are going to be displaying both the city scatter and the
                # text box
                self.visualization_elements_manager.add_city_scatter_and_text(new_vis_element)
                continue

            if plot_controller.should_display(vis_element=new_vis_element, display_type='map'):
                vis_elements.append(new_vis_element)
        return vis_elements

    def _fill_visualization_elements_with_polygons(self, visualization_elements_: list[
        visualization_elements.VisualizationElement]):
        for i, visualization_element in enumerate(visualization_elements_):
            logging.info(f"\tFilling visualization element {visualization_element} "
                         f"\n\t\tNumber {i} of {len(visualization_elements_)}")
            extra_args = visualization_element.__dict__
            poly = self.polygon_factory_.create_poly(vis_element=visualization_element,
                                                     **extra_args)

            visualization_element.default_poly = poly

    def _create_entities(self, entities_types: list, filter_same_city_visiting_assignments: bool = False):
        entities_ = self.entities_manager.get_all_entities(entities_types)
        if filter_same_city_visiting_assignments:
            entities_ = _remove_same_city_visiting_assignments(entities_=entities_)
        return entities_

    def _create_map(self, conditions_map, plot_controller, plot_manager):
        if not self.entities_:
            self.entities_ = self._create_entities(entities_types=[entities.City, entities.ProviderAssignment],
                                                   filter_same_city_visiting_assignments=True)
        vis_elements = self._convert_entities_to_vis_elements(entities_=self.entities_,
                                                              plot_controller=plot_controller,
                                                              conditions_map=conditions_map)
        self._fill_visualization_elements_with_polygons(visualization_elements_=vis_elements)
        self.visualization_elements_manager.add_visualization_elements(vis_elements)

        non_text_vis_elements = self.visualization_elements_manager.get_all([visualization_elements.CityScatter,
                                                                             visualization_elements.Line])
        non_text_results = [VisualizationElementResult(vis_element=non_text_vis_element) for non_text_vis_element in
                            non_text_vis_elements]
        plotted_elements = []
        for result in non_text_results:
            plotted = plot_manager.attempt_plot_algorithm_element(vis_element_result=result)
            if plotted:
                self.algorithm_handler.add_element_to_algorithm(element=result.vis_element)
                plotted_elements.append(result.vis_element)
        for city_scatter_and_text in self.visualization_elements_manager.city_scatter_and_texts.values():
            for vis_element_result in self.algorithm_handler.find_best_polygon(
                    city_element=city_scatter_and_text.city_scatter,
                    text_box_element=city_scatter_and_text.city_text_box,
                    city_buffer=self.config.get_config_value('algorithm.city_to_text_box_buffer', int),
                    number_of_steps=self.config.get_config_value('algorithm.search_steps', int),
                    polygon_to_vis_element=self.visualization_elements_manager.polygon_to_vis_element):
                self.visualization_elements_manager.fill_element(vis_element_result.vis_element)
                self.visualization_elements_manager.add_visualization_elements(visualization_elements_=[vis_element_result.vis_element])
                plotted = plot_manager.attempt_plot_algorithm_element(vis_element_result=vis_element_result)
                if plotted and type(vis_element_result.vis_element) in [CityScatter, Best, Line]:
                    plotted_elements.append(vis_element_result.vis_element)

        return plotted_elements

    def create_highest_volume_line_map(self, number_of_results: int):
        logging.info("Creating highest volume line map.")
        if not self.entities_:
            self.entities_ = self._create_entities(entities_types=[entities.City, entities.ProviderAssignment],
                                                   filter_same_city_visiting_assignments=True)
        highest_volume_cities = data_functions.get_top_volume_origin_cities(df=self.df,
                                                                            num_results=number_of_results)
        visiting_from_high_vol_city = set(
            entity.visiting_city_name for entity in self.entities_ if type(entity) is entities.ProviderAssignment and
            entity.origin_city_name in highest_volume_cities)
        all_plot_cities = set(highest_volume_cities) | visiting_from_high_vol_city
        conditions_map = plotting.HighestCityVisitingVolumeConditions(
            origin_cities=highest_volume_cities,
            all_plot_cities=all_plot_cities,
            config=self.config)
        vis_element_plot_controller = plotting.PlotController(
            config=self.config,
            show_visiting_text_boxes=False)
        plotter = plotting.PlotManager(algorithm_handler=self.algorithm_handler,
                                       map_plotter=self.map_plotter,
                                       plot_controller=vis_element_plot_controller)

        plotted_elements = self._create_map(conditions_map=conditions_map,
                                            plot_controller=vis_element_plot_controller,
                                            plot_manager=plotter)

        return plotted_elements

    def create_number_of_visiting_providers_map(self):
        logging.info("Creating number of providers by visiting site map.")

        conditions_map = plotting.NumberOfVisitingProvidersConditions(config=self.config)
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
