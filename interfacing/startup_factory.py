import pandas as pd
from typing import Callable

import environment_management
from things import entities


class StartupFactory:

    def __init__(self, df: pd.DataFrame, entities_manager: entities.EntitiesManager):
        self.df = df
        self.entities_manager = entities_manager

    def fill_entities_manager(self, coord_converter_func: Callable):
        entities_factory = environment_management.EntitiesFactory()
        entities_factory.fill_entities_manager(entities_manager=self.entities_manager,
                                               df=self.df,
                                               coord_converter=coord_converter_func)
        return entities_factory

    def create_polygon(self, entity: visualization_elements.Entity, environment: environment_management.Environment) -> dict:
        pass

