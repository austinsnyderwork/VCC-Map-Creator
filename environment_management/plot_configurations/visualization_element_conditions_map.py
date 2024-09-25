from abc import ABC
from collections.abc import Callable
from functools import wraps
import visualization_elements

import config_manager
from things.entities import entities


def apply_to_type(expected_type):
    def decorator(func):
        @wraps(func)
        def wrapper(self, entity, **kwargs):
            if not isinstance(entity, expected_type):
                return None
            return func(self, entity, **kwargs)
        return wrapper
    return decorator


class Condition:

    def __init__(self, condition: Callable, visualization_element: visualization_elements.VisualizationElement):
        self.condition = condition
        self.visualization_element = visualization_element


class ConditionsMap(ABC):

    def __init__(self, conditions: list[Condition]):
        self.conditional_visualization_elements = []
        self.conditions = conditions
        self.config = config_manager.ConfigManager()

    def get_visualization_element_for_condition(self, **kwargs):
        for condition in self.conditions:
            if condition.condition(**kwargs):
                return condition.visualization_element


class NumberOfVisitingClinicsConditions(ConditionsMap):

    def __init__(self):
        self.conditional_visualization_elements = [visualization_elements.CityScatter]
        condition_funcs = [self.range_1_condition,
                           self.range_2_condition,
                           self.range_3_condition,
                           self.range_4_condition]

        vis_elements_ = self._create_visualization_elements()
        conditions = [Condition(condition=condition_func, visualization_element=vis_element) for condition_func, vis_element in
                      zip(condition_funcs, vis_elements_)]

        super().__init__(conditions=conditions)

    def _create_visualization_elements(self):
        visualization_element_1 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_clinics.range_1_size', int),
            color=self.config.get_config_value('num_visiting_clinics.range_1_color', str)
        )
        visualization_element_2 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_clinics.range_2_size', int),
            color=self.config.get_config_value('num_visiting_clinics.range_2_color', str)
        )
        visualization_element_3 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_clinics.range_3_size', int),
            color=self.config.get_config_value('num_visiting_clinics.range_3_color', str)
        )
        visualization_element_4 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_clinics.range_4_size', int),
            color=self.config.get_config_value('num_visiting_clinics.range_4_color', str)
        )
        visualization_elements_ = [visualization_element_1, visualization_element_2, visualization_element_3, visualization_element_4]
        return visualization_elements_

    @apply_to_type(entities.City)
    def range_1_condition(self, entity: entities.Entity, **kwargs):
        range_1_min = self.config.get_config_value('num_visiting_clinics.range_1_min', int)
        range_1_max = self.config.get_config_value('num_visiting_clinics.range_1_max', int)

        return range_1_min < len(entity.visiting_clinics) < range_1_max

    @apply_to_type(entities.City)
    def range_2_condition(self, entity: entities.Entity, **kwargs):
        range_2_min = self.config.get_config_value('num_visiting_clinics.range_2_min', int)
        range_2_max = self.config.get_config_value('num_visiting_clinics.range_2_max', int)

        return range_2_min < len(entity.visiting_clinics) < range_2_max

    @apply_to_type(entities.City)
    def range_3_condition(self, entity: entities.Entity, **kwargs):
        range_3_min = self.config.get_config_value('num_visiting_clinics.range_3_min', int)
        range_3_max = self.config.get_config_value('num_visiting_clinics.range_3_max', int)

        return range_3_min < len(entity.visiting_clinics) < range_3_max

    @apply_to_type(entities.City)
    def range_4_condition(self, entity: entities.Entity, **kwargs):
        range_4_min = self.config.get_config_value('num_visiting_clinics.range_4_min', int)
        range_4_max = 1e5

        return range_4_min < len(entity.visiting_clinics) < range_4_max


class HighestCityVisitingVolumeConditions(ConditionsMap):

    def __init__(self, highest_volume_cities: list[str]):
        self.conditional_visualization_elements = [visualization_elements.CityScatter]
        condition_funcs = [self.city_condition, self.line_condition]
        visualization_elements_ = self._create_visualization_elements()
        conditions = [Condition(condition=condition_func, visualization_element=visualization_element) for condition_func, visualization_element in
                      zip(condition_funcs, visualization_elements_)]

        super().__init__(conditions)
        self.highest_volume_cities = highest_volume_cities

    def _create_visualization_elements(self):
        visualization_element_1 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_providers.range_1_size', int),
            color=self.config.get_config_value('num_visiting_providers.range_1_color', str)
        )
        visualization_elements_ = [visualization_element_1]
        return visualization_elements_

    @apply_to_type(entities.City)
    def city_condition(self, entity: entities.Entity):
        return entity.name in self.highest_volume_cities

    @apply_to_type(entities.ProviderAssignment)
    def line_condition(self, entity: entities.Entity):
        return entity.origin_site.city_name in self.highest_volume_cities or entity.visiting_site.city_name in self.highest_volume_cities


class NumberOfVisitingProvidersConditions(ConditionsMap):

    def __init__(self):
        self.conditional_visualization_elements = [visualization_elements.CityScatter]
        condition_funcs = [self.range_1_condition,
                           self.range_2_condition,
                           self.range_3_condition,
                           self.range_4_condition]

        vis_elements_ = self._create_visualization_elements()
        conditions = [Condition(condition=condition_func, visualization_element=vis_element) for condition_func, vis_element in
                      zip(condition_funcs, vis_elements_)]

        super().__init__(conditions=conditions)

    def _create_visualization_elements(self):
        visualization_element_1 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_providers.range_1_size', int),
            color=self.config.get_config_value('num_visiting_providers.range_1_color', str)
        )
        visualization_element_2 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_providers.range_2_size', int),
            color=self.config.get_config_value('num_visiting_providers.range_2_color', str)
        )
        visualization_element_3 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_providers.range_3_size', int),
            color=self.config.get_config_value('num_visiting_providers.range_3_color', str)
        )
        visualization_element_4 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_providers.range_4_size', int),
            color=self.config.get_config_value('num_visiting_providers.range_4_color', str)
        )
        visualization_elements_ = [visualization_element_1, visualization_element_2, visualization_element_3, visualization_element_4]
        return visualization_elements_

    @apply_to_type(entities.City)
    def range_1_condition(self, entity: entities.Entity, **kwargs):
        range_1_min = self.config.get_config_value('num_visiting_providers.range_1_min', int)
        range_1_max = self.config.get_config_value('num_visiting_providers.range_1_max', int)

        return range_1_min < len(entity.visiting_providers) < range_1_max

    @apply_to_type(entities.City)
    def range_2_condition(self, entity: entities.Entity, **kwargs):
        range_2_min = self.config.get_config_value('num_visiting_providers.range_2_min', int)
        range_2_max = self.config.get_config_value('num_visiting_providers.range_2_max', int)

        return range_2_min < len(entity.visiting_providers) < range_2_max

    @apply_to_type(entities.City)
    def range_3_condition(self, entity: entities.Entity, **kwargs):
        range_3_min = self.config.get_config_value('num_visiting_providers.range_3_min', int)
        range_3_max = self.config.get_config_value('num_visiting_providers.range_3_max', int)

        return range_3_min < len(entity.visiting_providers) < range_3_max

    @apply_to_type(entities.City)
    def range_4_condition(self, entity: entities.Entity, **kwargs):
        range_4_min = self.config.get_config_value('num_visiting_providers.range_4_min', int)
        range_4_max = 1e5

        return range_4_min < len(entity.visiting_providers) < range_4_max


class NumberOfVisitingSpecialtiesConditions(ConditionsMap):

    def __init__(self):
        self.conditional_visualization_elements = [visualization_elements.CityScatter]
        condition_funcs = [self.range_1_condition,
                           self.range_2_condition,
                           self.range_3_condition]
        visualization_elements_ = self._create_visualization_elements()
        conditions = [Condition(condition=condition_func, visualization_element=visualization_element) for condition_func, visualization_element in
                      zip(condition_funcs, visualization_elements_)]

        super().__init__(conditions)

    def _create_visualization_elements(self):
        visualization_element_1 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_specialties.range_1_size', int),
            color=self.config.get_config_value('num_visiting_specialties.range_1_color', str)
        )
        visualization_element_2 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_specialties.range_2_size', int),
            color=self.config.get_config_value('num_visiting_specialties.range_2_color', str)
        )
        visualization_element_3 = visualization_elements.CityScatter(
            size=self.config.get_config_value('num_visiting_specialties.range_3_size', int),
            color=self.config.get_config_value('num_visiting_specialties.range_3_color', str)
        )
        visualization_elements_ = [visualization_element_1, visualization_element_2, visualization_element_3]
        return visualization_elements_

    def range_1_condition(self, entity: entities.Entity, **kwargs):
        range_1_min = self.config.get_config_value('num_visiting_specialties.range_1_min', int)
        range_1_max = self.config.get_config_value('num_visiting_specialties.range_1_max', int)

        return range_1_min < len(entity.visiting_specialties) < range_1_max

    def range_2_condition(self, entity: entities.Entity, **kwargs):
        range_2_min = self.config.get_config_value('num_visiting_specialties.range_2_min', int)
        range_2_max = self.config.get_config_value('num_visiting_specialties.range_2_max', int)

        return range_2_min < len(entity.visiting_specialties) < range_2_max

    def range_3_condition(self, entity: entities.Entity, **kwargs):
        range_3_min = self.config.get_config_value('num_visiting_specialties.range_3_min', int)
        range_3_max = self.config.get_config_value('num_visiting_specialties.range_3_max', int)

        return range_3_min < len(entity.visiting_specialties) < range_3_max
