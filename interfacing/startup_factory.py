import pandas as pd
from typing import Callable

import environment_management
from environment_management import CityOriginNetworkHandler
from things import entities
from things import visualization_elements


class StartupFactory:

    def __init__(self, df: pd.DataFrame, entities_manager: entities.EntitiesManager,
                 city_origin_network_handler: CityOriginNetworkHandler):
        self.city_origin_network_handler = city_origin_network_handler
        self.df = df
        self.entities_manager = entities_manager

    def fill_entities_manager(self, coord_converter_func: Callable):
        entities_factory = environment_management.EntitiesFactory()
        entities_factory.fill_entities_manager(entities_manager=self.entities_manager,
                                               df=self.df,
                                               coord_converter=coord_converter_func)
        return entities_factory

    def fill_city_origin_networks(self):
        for provider_assignment in self.entities_manager.get_all_entities(entities.ProviderAssignment):
            self.city_origin_network_handler.add_city_origin_network(origin_city=provider_assignment.origin_city)
        for provider_assignment in self.entities_manager.get_all_entities(entities.ProviderAssignment):
            self.city_origin_network_handler.add_visiting_city(origin_city=provider_assignment.origin_city,
                                                               visiting_city=provider_assignment.visiting_city)

