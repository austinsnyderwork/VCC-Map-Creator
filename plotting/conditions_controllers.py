import copy
import logging
from abc import ABC
from collections.abc import Callable
from typing import Union

from entities.entity_classes import ProviderAssignment, City
from entities.factory import EntitiesContainer
from visualization_elements.element_classes import VisualizationElement, CityScatter, TextBox, Line, ScatterAttributes


class _Condition:

    def __init__(self,
                 should_apply: Callable,
                 apply_func: Callable,
                 applicable_entity_type: type(VisualizationElement)
                 ):
        self.should_apply = should_apply
        self.apply_func = apply_func

        self.applicable_element_type = applicable_entity_type


class _ConditionsMap:

    def __init__(self):
        self.map = {
            CityScatter: [],
            TextBox: [],
            Line: []
        }

    def add_condition(self, condition: _Condition):
        self.map[condition.applicable_element_type].append(condition)


class ConditionsController(ABC):

    def __init__(self, conditions: list[_Condition], **kwargs):
        self.conditions = self._create_conditions_map(conditions=conditions)
        self.entity_types = []

        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def _create_conditions_map(conditions) -> _ConditionsMap:
        conditions_map = _ConditionsMap()
        for condition in conditions:
            conditions_map.add_condition(condition)

        return conditions_map


class NumberOfVisitingClinicsConditionsController(ConditionsController):

    def __init__(self, config, **kwargs):
        self.config = config

        super().__init__(conditions=self._create_conditions())

    def _range_1_condition(self, city: City, **kwargs):
        range_1_min = self.config('num_visiting_clinics.range_1_min', int)
        range_1_max = self.config('num_visiting_clinics.range_1_max', int)

        return range_1_min < len(city.visiting_clinics) < range_1_max

    def _range_2_condition(self, city: City, **kwargs):
        range_2_min = self.config.get_config_value('num_visiting_clinics.range_2_min', int)
        range_2_max = self.config.get_config_value('num_visiting_clinics.range_2_max', int)

        return range_2_min < len(city.visiting_clinics) < range_2_max

    def _range_3_condition(self, city: City, **kwargs):
        range_3_min = self.config.get_config_value('num_visiting_clinics.range_3_min', int)
        range_3_max = self.config.get_config_value('num_visiting_clinics.range_3_max', int)

        return range_3_min < len(city.visiting_clinics) < range_3_max

    def _range_4_condition(self, city: City, **kwargs):
        range_4_min = self.config.get_config_value('num_visiting_clinics.range_4_min', int)
        range_4_max = 1e5

        return range_4_min < len(city.visiting_clinics) < range_4_max

    def _create_conditions(self) -> list[_Condition]:
        conditions = []

        vis_element_1 = CityScatter(
            map_attributes={
                ScatterAttributes.RADIUS: self.config('num_visiting_clinics.range_1_scatter_radius', int),
                ScatterAttributes.COLOR: self.config('num_visiting_clinics.range_1_color', str)
            }
        )
        conditions.append(
            _Condition(
                should_apply=self._range_1_condition,
                apply_func=lambda: vis_element_1,
                applicable_entity_type=City,
            )
        )

        vis_element_2 = CityScatter(
            map_attributes = {
                ScatterAttributes.RADIUS: self.config('num_visiting_clinics.range_2_scatter_size', int),
                ScatterAttributes.COLOR: self.config('num_visiting_clinics.range_2_color', str)
            }
        )
        conditions.append(
            _Condition(
                should_apply=self._range_2_condition,
                apply_func=lambda: vis_element_2,
                applicable_entity_type=City,
            )
        )

        vis_element_3 = CityScatter(
            map_attributes={
                ScatterAttributes.RADIUS: self.config('num_visiting_clinics.range_3_scatter_size', int),
                ScatterAttributes.COLOR: self.config('num_visiting_clinics.range_3_color', str)
            }
        )
        conditions.append(
            _Condition(
                should_apply=self._range_3_condition,
                apply_func=lambda: vis_element_3,
                applicable_entity_type=City,
            )
        )

        vis_element_4 = CityScatter(
            map_attributes={
                ScatterAttributes.RADIUS: self.config('num_visiting_clinics.range_4_scatter_size', int),
                ScatterAttributes.COLOR: self.config('num_visiting_clinics.range_4_color', str)
            }
        )
        conditions.append(
            _Condition(
                should_apply=self._range_4_condition,
                apply_func=lambda: vis_element_4,
                applicable_entity_type=City,
            )
        )

        return conditions


class HighestOriginVolumeController(ConditionsController):

    def __init__(self, entities_container: EntitiesContainer, origin_cities_limit: int, **kwargs):
        self._entities_container = self._filter_entities_container(entities_container=entities_container,
                                                                   origin_cities_limit=origin_cities_limit)
        
        conditions = [
            _Condition(condition=condition_func, visualization_element=visualization_element)
            for condition_func, visualization_element in zip(condition_funcs, visualization_elements_)
        ]
        super().__init__(conditions)

        self.conditions = conditions
        self.entity_types = [City, ProviderAssignment]
    
    @staticmethod
    def _filter_entities_container(entities_container: EntitiesContainer, origin_cities_limit: int):
        # Volume (int) : set(City, City, City)
        city_volumes = dict()
        for city in entities_container.cities:
            num_worksites = len(city.worksites)
            if num_worksites not in city_volumes:
                city_volumes[num_worksites] = set()

            city_volumes[num_worksites].add(city)

        highest_volumes = sorted(list(city_volumes.keys()), reverse=True)[:5]
        origin_cities = set()
        for volume in highest_volumes:
            origin_cities.update(city_volumes[volume])
            if len(origin_cities) >= origin_cities_limit:
                break

        # Filter EntitiesContainer based on the high volume origin cities
        entities_container = copy.deepcopy(entities_container)
        valid_provider_assignments = set(
            pa for pa in entities_container.provider_assignments
            if pa.origin_city in origin_cities
        )
        entities_container.provider_assignments = valid_provider_assignments
        valid_cities = set()
        valid_worksites = set()
        for pa in valid_provider_assignments:
            valid_cities.add(pa.origin_city)
            valid_cities.add(pa.visiting_city)

            valid_worksites.add(pa.origin_site)
            valid_worksites.add(pa.visiting_site)
        entities_container.cities = valid_cities
        entities_container.worksites = valid_worksites
        
        return entities_container

    def _create_visualization_elements(self, config, visualization_element_data: dict):
        visualization_element_1a = CityScatter(
            size=config.get_config_value('num_visiting_providers.range_1_scatter_size', int),
            color=config.get_config_value('num_visiting_providers.range_1_color', str)
        )
        if visualization_element_data and CityScatter in visualization_element_data:
            for k, v in visualization_element_data[CityScatter].items():
                setattr(visualization_element_1a, k, v)
        visualization_element_1b = CityTextBox()
        vis_element_1 = CityScatterAndText(city_scatter=visualization_element_1a,
                                           city_text_box=visualization_element_1b)

        visualization_element_2 = Line()
        if visualization_element_data and Line in visualization_element_data:
            for k, v in visualization_element_data[Line].items():
                setattr(visualization_element_2, k, v)
        visualization_elements_ = [vis_element_1, visualization_element_2]
        return visualization_elements_

    @apply_to_type(City)
    def city_condition(self, entity: Entity, **kwargs):
        return entity.city_name in self.all_plot_cities

    @apply_to_type(ProviderAssignment)
    def line_condition(self, entity: Entity, **kwargs):
        return entity.origin_city_name in self.origin_cities


class NumberOfVisitingProvidersConditionsController(ConditionsController):

    def __init__(self, config):
        condition_funcs = [self.range_1_condition,
                           self.range_2_condition,
                           self.range_3_condition,
                           self.range_4_condition]
        visualization_elements_ = self._create_visualization_elements(config=config)
        conditions = [_Condition(condition=condition_func, visualization_element=visualization_element) for
                      condition_func, visualization_element in
                      zip(condition_funcs, visualization_elements_)]
        super().__init__(conditions)

        self.conditions = conditions
        self.config = config
        self.entity_types = [City]

    def _create_visualization_elements(self, config) -> Union[list[CityScatter], list[CityScatterAndText]]:
        visualization_element_1a = CityScatter(
            size=config.get_config_value('num_visiting_providers.range_1_scatter_size', int),
            color=config.get_config_value('num_visiting_providers.range_1_color', str)
        )
        vis_element_1b = CityTextBox()
        csat_1 = CityScatterAndText(city_scatter=visualization_element_1a,
                                    city_text_box=vis_element_1b)

        visualization_element_2a = CityScatter(
            size=config.get_config_value('num_visiting_providers.range_2_scatter_size', int),
            color=config.get_config_value('num_visiting_providers.range_2_color', str)
        )
        vis_element_2b = CityTextBox()
        csat_2 = CityScatterAndText(city_scatter=visualization_element_2a,
                                    city_text_box=vis_element_2b)

        visualization_element_3a = CityScatter(
            size=config.get_config_value('num_visiting_providers.range_3_scatter_size', int),
            color=config.get_config_value('num_visiting_providers.range_3_color', str)
        )
        vis_element_3b = CityTextBox()
        csat_3 = CityScatterAndText(city_scatter=visualization_element_3a,
                                    city_text_box=vis_element_3b)
        
        visualization_element_4a = CityScatter(
            size=config.get_config_value('num_visiting_providers.range_4_scatter_size', int),
            color=config.get_config_value('num_visiting_providers.range_4_color', str)
        )
        vis_element_4b = CityTextBox()
        csat_4 = CityScatterAndText(city_scatter=visualization_element_4a,
                                    city_text_box=vis_element_4b)
        
        visualization_elements_ = [csat_1, csat_2, csat_3, csat_4]
        return visualization_elements_

    @apply_to_type(City)
    def range_1_condition(self, entity: Entity, **kwargs):
        range_1_min = self.config.get_config_value('num_visiting_providers.range_1_min', int)
        range_1_max = self.config.get_config_value('num_visiting_providers.range_1_max', int)

        logging.info(f"Found {len(entity.visiting_providers)} visiting providers for {entity.city_name}")
        return range_1_min < len(entity.visiting_providers) < range_1_max

    @apply_to_type(City)
    def range_2_condition(self, entity: Entity, **kwargs):
        range_2_min = self.config.get_config_value('num_visiting_providers.range_2_min', int)
        range_2_max = self.config.get_config_value('num_visiting_providers.range_2_max', int)

        return range_2_min < len(entity.visiting_providers) < range_2_max

    @apply_to_type(City)
    def range_3_condition(self, entity: Entity, **kwargs):
        range_3_min = self.config.get_config_value('num_visiting_providers.range_3_min', int)
        range_3_max = self.config.get_config_value('num_visiting_providers.range_3_max', int)

        return range_3_min < len(entity.visiting_providers) < range_3_max

    @apply_to_type(City)
    def range_4_condition(self, entity: Entity, **kwargs):
        range_4_min = self.config.get_config_value('num_visiting_providers.range_4_min', int)
        range_4_max = 1e5

        return range_4_min < len(entity.visiting_providers) < range_4_max


class NumberOfVisitingSpecialtiesConditionsController(ConditionsController):

    def __init__(self, config):
        self.config = config
        self.entity_types = [City]
        condition_funcs = [self.range_1_condition,
                           self.range_2_condition,
                           self.range_3_condition]
        visualization_elements_ = self._create_visualization_elements()
        conditions = [_Condition(condition=condition_func, visualization_element=visualization_element) for condition_func, visualization_element in
                      zip(condition_funcs, visualization_elements_)]

        super().__init__(conditions)

    def _create_visualization_elements(self):
        visualization_element_1 = CityScatter(
            size=self.config.get_config_value('num_visiting_specialties.range_1_scatter_size', int),
            color=self.config.get_config_value('num_visiting_specialties.range_1_color', str)
        )
        visualization_element_2 = CityScatter(
            size=self.config.get_config_value('num_visiting_specialties.range_2_scatter_size', int),
            color=self.config.get_config_value('num_visiting_specialties.range_2_color', str)
        )
        visualization_element_3 = CityScatter(
            size=self.config.get_config_value('num_visiting_specialties.range_3_scatter_size', int),
            color=self.config.get_config_value('num_visiting_specialties.range_3_color', str)
        )
        visualization_elements_ = [visualization_element_1, visualization_element_2, visualization_element_3]
        return visualization_elements_

    def range_1_condition(self, entity: Entity, **kwargs):
        range_1_min = self.config.get_config_value('num_visiting_specialties.range_1_min', int)
        range_1_max = self.config.get_config_value('num_visiting_specialties.range_1_max', int)

        return range_1_min < len(entity.visiting_specialties) < range_1_max

    def range_2_condition(self, entity: Entity, **kwargs):
        range_2_min = self.config.get_config_value('num_visiting_specialties.range_2_min', int)
        range_2_max = self.config.get_config_value('num_visiting_specialties.range_2_max', int)

        return range_2_min < len(entity.visiting_specialties) < range_2_max

    def range_3_condition(self, entity: Entity, **kwargs):
        range_3_min = self.config.get_config_value('num_visiting_specialties.range_3_min', int)
        range_3_max = self.config.get_config_value('num_visiting_specialties.range_3_max', int)

        return range_3_min < len(entity.visiting_specialties) < range_3_max
