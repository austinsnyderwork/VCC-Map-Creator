from visual_elements.element_classes import (AlgorithmClassification, VisualElement,
                                             VisualElementAttributes)


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
            show=False,
            facecolor='brown',
            edgecolor='brown',
            transparency=1,
            immediately_remove=True,
            center_view=False,
            zorder=4
        ),
        AlgorithmClassification.TEXT_SCAN: VisualElementAttributes(
            show=False,
            facecolor="blue",
            transparency=1,
            immediately_remove=True,
            center_view=False,
            steps_to_show=1,
            zorder=3,
        ),
        AlgorithmClassification.TEXT_FINALIST: VisualElementAttributes(
            show=False,
            facecolor="purple",
            transparency=1.0,
            immediately_remove=True,
            center_view=False,
            steps_to_show=1,
            zorder=3,
        ),
        AlgorithmClassification.TEXT_BEST: VisualElementAttributes(
            show=True,
            facecolor='green',
            transparency=1.0,
            immediately_remove=False,
            center_view=False,
            steps_to_show=1,
            zorder=3
        )
    }

    @classmethod
    def resolve_algo_attributes(cls,
                                visual_element: VisualElement,
                                classification
                                ) -> VisualElementAttributes:
        attributes = VisualElementAttributes()
        if classification in cls._algo_defaults:
            algo_defaults = cls._algo_defaults[classification]
            attributes.update(algo_defaults)

        attributes.update(visual_element.algo_attributes)

        return attributes


