from typing import Optional

from visual_elements.element_classes import (AlgorithmClassification, VisualElement,
                                             CityScatter, Line, TextBox, VisualElementAttributes)


class VisualElementAttributesResolver:
    _algo_defaults = {
        AlgorithmClassification.LINE: VisualElementAttributes(
            show=True,
            transparency=1,
            immediately_remove=False,
            center_view=False,
            zorder=1
        ),
        AlgorithmClassification.CITY_SCATTER: VisualElementAttributes(
            show=True,
            transparency=1,
            immediately_remove=False,
            center_view=False,
            zorder=2
        ),
        AlgorithmClassification.INTERSECT: VisualElementAttributes(
            show=True,
            facecolor='brown',
            transparency=1,
            immediately_remove=True,
            center_view=False,
            zorder=4
        ),
        AlgorithmClassification.TEXT_SCAN: VisualElementAttributes(
            show=True,
            facecolor="blue",
            transparency=1,
            immediately_remove=False,
            center_view=False,
            steps_to_show=1,
            zorder=3,
        ),
        AlgorithmClassification.TEXT_FINALIST: VisualElementAttributes(
            show=True,
            facecolor="purple",
            transparency=1.0,
            immediately_remove=False,
            center_view=False,
            steps_to_show=1,
            zorder=3,
        )
    }

    @classmethod
    def resolve_algo_attributes(cls, element: VisualElement, classification) -> VisualElementAttributes:
        attributes = VisualElementAttributes()
        if classification in cls._algo_defaults:
            algo_defaults = cls._algo_defaults[classification]
            attributes.update(algo_defaults)

        attributes.update(element.algo_attributes)

        return attributes


