
from visual_elements.element_classes import VisualElement
from visual_elements_config import algo_config, DisplayConfig


class VisualElementAttributesFiller:

    @staticmethod
    def _apply_attributes(vis_element: VisualElement, attributes: dict):
        for k, v in attributes.items():
            if not hasattr(vis_element, k):
                setattr(vis_element, k, v)

    @classmethod
    def fill_element(cls, vis_element):
        ele_type = type(vis_element)
        if ele_type in algo_config:
            general_attributes = {k: v for k, v in algo_config[ele_type].items() if isinstance(k, str)}

            if isinstance(algo_config[ele_type], DisplayConfig):
                cls._apply_attributes(vis_element=vis_element,
                                      attributes=algo_config[vis_element].attributes)
                return

            # Classification-specific attributes take priority over general class attributes, so we apply these
            # after searching for those classification-specific attributes
            cls._apply_attributes(vis_element=vis_element,
                                  attributes=general_attributes)

            if not hasattr(vis_element, 'classification'):
                return

            if vis_element.classification not in algo_config[ele_type]:
                return

            display_config = algo_config[ele_type]
            cls._apply_attributes(vis_element=vis_element,
                                  attributes=display_config.attributes)

