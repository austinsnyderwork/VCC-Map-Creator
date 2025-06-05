from abc import ABC
from collections.abc import Callable

from visual_elements.element_classes import VisualElement

from entities.entity_classes import ProviderAssignment, City


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
            ProviderAssignment: []
        }

    def add_condition(self, condition: Callable, entity_type):
        self.conditions[entity_type].append(condition)


class ConditionsController(ABC):

    def __init__(self, conditions_map: ConditionsMap, **kwargs):
        self._conditions_map = conditions_map

        for k, v in kwargs.items():
            setattr(self, k, v)

    def determine_visual_element(self, entity) -> VisualElement:
        conditions = self._conditions_map.conditions[type(entity)]
        vis_elements = [ve for condition in conditions if (ve := condition(entity)) is not None]

        if len(vis_elements) >= 2:
            raise ValueError(f"Fetched multiple different visualization elements for entity type {type(entity)}")

        return vis_elements[0] if vis_elements else None


