from abc import ABC
from collections.abc import Callable

from entities.entity_classes import ProviderAssignment, City, Provider, Worksite
from environment_management.city_origin_networks import CityNetworksHandler
from visual_elements.element_classes import VisualElement


class _Condition:

    def __init__(self,
                 should_apply: Callable,
                 visual_element: VisualElement,
                 applicable_entity_type: type(VisualElement)
                 ):
        self.should_apply = should_apply
        self.visual_element = visual_element

        self.applicable_element_type = applicable_entity_type


class ConditionsMap:

    def __init__(self):
        self.conditions = {
            City: [],
            ProviderAssignment: [],
            Provider: [],
            Worksite: []
        }

    def add_condition(self, condition: Callable, entity_type):
        self.conditions[entity_type].append(condition)


class ConditionsController(ABC):

    def __init__(self,
                 conditions_map: ConditionsMap,
                 city_networks_handler: CityNetworksHandler,
                 **kwargs):
        self._conditions_map = conditions_map
        self._city_networks_handler = city_networks_handler

        for k, v in kwargs.items():
            setattr(self, k, v)

    def determine_visual_elements(self, entity) -> list[VisualElement]:
        conditions = self._conditions_map.conditions[type(entity)]
        vis_elements = [
            ve
            for condition in conditions
            for ve in condition(entity)
        ]

        return vis_elements
