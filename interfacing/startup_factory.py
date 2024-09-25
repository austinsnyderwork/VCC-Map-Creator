import pandas as pd
from typing import Callable

from . import helper_functions
import entities
import environment_management


class StartupFactory:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_filled_environment(self, coord_converter_func: Callable):
        environment_factory = environment_management.EnvironmentFactory()
        cities_directory = entities.CitiesDirectory()
        colors = helper_functions.get_colors()
        city_origin_network_handler_ = environment_management.CityOriginNetworkHandler(colors=colors)
        environment = environment_management.Environment(cities_directory=cities_directory,
                                                         city_origin_network_handler=city_origin_network_handler_)
        environment_factory.fill_environment(df=self.df,
                                             environment=environment,
                                             coord_converter=coord_converter_func)
        return environment

    def create_polygon(self, entity: entities.Entity, environment: environment_management.Environment) -> dict:
        pass

