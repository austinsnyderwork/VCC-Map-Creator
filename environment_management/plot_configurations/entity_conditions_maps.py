from collections.abc import Callable
import entities

from utils.helper_functions import get_config_value


class Condition:

    def __init__(self, condition: Callable, entity: entities.Entity):
        self.condition = condition
        self.entity = entity


class ConditionsMap:

    def __init__(self, conditions: list[Condition]):
        self.conditions = conditions

    def get_entity_for_condition(self, **kwargs):
        for condition in self.conditions:
            if condition.condition(**kwargs):
                return condition.entity


class NumberOfVisitingClinicsConditions(ConditionsMap):

    def __init__(self, config):
        condition_funcs = [self.range_1_condition,
                           self.range_2_condition,
                           self.range_3_condition,
                           self.range_4_condition]

        entities_ = self.create_entities()
        conditions = [Condition(condition=condition_func, entity=entity) for condition_func, entity in
                      zip(condition_funcs, entities_)]

        super().__init__(conditions=conditions)
        self.config = config

    def create_entities(self):
        entity_1 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_clinics.range_1_size', int),
            color=get_config_value(self.config, 'num_visiting_clinics.range_1_color', str)
        )
        entity_2 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_clinics.range_2_size', int),
            color=get_config_value(self.config, 'num_visiting_clinics.range_2_color', str)
        )
        entity_3 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_clinics.range_3_size', int),
            color=get_config_value(self.config, 'num_visiting_clinics.range_3_color', str)
        )
        entity_4 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_clinics.range_4_size', int),
            color=get_config_value(self.config, 'num_visiting_clinics.range_4_color', str)
        )
        entities_ = [entity_1, entity_2, entity_3, entity_4]
        return entities_

    def range_1_condition(self, num_visiting_clinics: int, **kwargs):
        range_1_min = get_config_value(self.config, 'num_visiting_clinics.range_1_min', int)
        range_1_max = get_config_value(self.config, 'num_visiting_clinics.range_1_max', int)

        return range_1_min < num_visiting_clinics < range_1_max

    def range_2_condition(self, num_visiting_clinics: int, **kwargs):
        range_2_min = get_config_value(self.config, 'num_visiting_clinics.range_2_min', int)
        range_2_max = get_config_value(self.config, 'num_visiting_clinics.range_2_max', int)

        return range_2_min < num_visiting_clinics < range_2_max

    def range_3_condition(self, num_visiting_clinics: int, **kwargs):
        range_3_min = get_config_value(self.config, 'num_visiting_clinics.range_3_min', int)
        range_3_max = get_config_value(self.config, 'num_visiting_clinics.range_3_max', int)

        return range_3_min < num_visiting_clinics < range_3_max

    def range_4_condition(self, num_visiting_clinics: int, **kwargs):
        range_4_min = get_config_value(self.config, 'num_visiting_clinics.range_4_min', int)
        range_4_max = 1e5

        return range_4_min < num_visiting_clinics < range_4_max


class NumberOfVisitingProvidersConditions(ConditionsMap):

    def __init__(self, config, highest_volume_cities: list[str]):
        condition_funcs = [self.condition]
        entities_ = self.create_entities()
        conditions = [Condition(condition=condition_func, entity=entity) for condition_func, entity in
                      zip(condition_funcs, entities_)]

        super().__init__(conditions)
        self.config = config
        self.highest_volume_cities = highest_volume_cities

    def create_entities(self):
        entity_1 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_providers.range_1_size', int),
            color=get_config_value(self.config, 'num_visiting_providers.range_1_color', str)
        )
        entities_ = [entity_1]
        return entities_

    def condition(self, city: entities.City):
        return city.name in self.highest_volume_cities


class NumberOfVisitingSpecialtiesConditions(ConditionsMap):

    def __init__(self, config):
        condition_funcs = [self.range_1_condition,
                           self.range_2_condition,
                           self.range_3_condition]
        entities_ = self.create_entities()
        conditions = [Condition(condition=condition_func, entity=entity) for condition_func, entity in
                      zip(condition_funcs, entities_)]

        super().__init__(conditions)
        self.config = config

    def create_entities(self):
        entity_1 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_specialties.range_1_size', int),
            color=get_config_value(self.config, 'num_visiting_specialties.range_1_color', str)
        )
        entity_2 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_specialties.range_2_size', int),
            color=get_config_value(self.config, 'num_visiting_specialties.range_2_color', str)
        )
        entity_3 = entities.CityScatter(
            size=get_config_value(self.config, 'num_visiting_specialties.range_3_size', int),
            color=get_config_value(self.config, 'num_visiting_specialties.range_3_color', str)
        )
        entities_ = [entity_1, entity_2, entity_3]
        return entities_

    def range_1_condition(self, num_visiting_specialties: int, **kwargs):
        range_1_min = get_config_value(self.config, 'num_visiting_specialties.range_1_min', int)
        range_1_max = get_config_value(self.config, 'num_visiting_specialties.range_1_max', int)

        return range_1_min < num_visiting_specialties < range_1_max

    def range_2_condition(self, num_visiting_specialties: int, **kwargs):
        range_2_min = get_config_value(self.config, 'num_visiting_specialties.range_2_min', int)
        range_2_max = get_config_value(self.config, 'num_visiting_specialties.range_2_max', int)

        return range_2_min < num_visiting_specialties < range_2_max

    def range_3_condition(self, num_visiting_specialties: int, **kwargs):
        range_3_min = get_config_value(self.config, 'num_visiting_specialties.range_3_min', int)
        range_3_max = get_config_value(self.config, 'num_visiting_specialties.range_3_max', int)

        return range_3_min < num_visiting_specialties < range_3_max
