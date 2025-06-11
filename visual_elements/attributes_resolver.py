from typing import Optional

from visual_elements.element_classes import (VisualElementClassification, TextBoxClassification, VisualElement,
                                             CityScatter, SearchArea, Line, TextBox, VisualElementAttributes)


class VisualElementAttributesResolver:
    _ve_algo_defaults = {
        VisualElementClassification.INTERSECT: VisualElementAttributes(
            show=True,
            facecolor='black',
            transparency=0.5,
            immediately_remove=True,
            center_view=False,
            fontsize=0.05,
            fontweight='normal',
            zorder=4
        )
    }

    _algo_defaults = {
        TextBox: {
            None: VisualElementAttributes(
                fontsize=0.2,
                fontweight="normal",
                show=True,
                facecolor="blue",
                transparency=0.5,
                immediately_remove=True,
                center_view=False,
                steps_to_show=5,
                zorder=2,
            ),
            TextBoxClassification.BEST: VisualElementAttributes(
                fontsize=0.2,
                fontweight="normal",
                show=True,
                facecolor="black",
                transparency=0.75,
                immediately_remove=False,
                center_view=False,
                zorder=2,
            ),
            TextBoxClassification.FINALIST: VisualElementAttributes(
                fontsize=0.2,
                fontweight="normal",
                show=True,
                facecolor="purple",
                transparency=1.0,
                immediately_remove=True,
                center_view=False,
                steps_to_show=1,
                zorder=2,
            ),
            TextBoxClassification.SCAN: VisualElementAttributes(
                fontsize=0.2,
                fontweight="normal",
                show=True,
                facecolor="blue",
                transparency=0.5,
                immediately_remove=False,
                center_view=True,
                steps_to_show=5,
                zorder=2,
            ),
        },
        CityScatter: {
            None: VisualElementAttributes(
                radius=0.2,
                show=True,
                facecolor='purple',
                edgecolor='pink',
                transparency=1.0,
                immediately_remove=False,
                center_view=False,
                marker='o',
                zorder=3,
                label='algo_label'
            )
        },
        Line: {
            None: VisualElementAttributes(
                show=True,
                color='blue',
                transparency=1.0,
                immediately_remove=False,
                center_view=False,
                linestyle='-',
                linewidth=0.2,
                zorder=1
            )
        }
    }

    _map_defaults = {
        TextBox: VisualElementAttributes(
            fontsize=0.2,
            font='Roboto',
            fontweight='normal',
            fontcolor='black',
            zorder=1
        ),
        Line: VisualElementAttributes(
            zorder=0,
            linewidth=0.2,
            linestyle='-',
            facecolor='pink'
        ),
        CityScatter: VisualElementAttributes(
            zorder=2,
            facecolor='pink',
            marker='o',
            edgecolor='yellow',
            size=0.2,
            label=''
        )
    }

    @classmethod
    def resolve_map_attributes(cls, element: VisualElement) -> VisualElementAttributes:
        map_attributes = cls._map_defaults.get(type(element), None)
        if not map_attributes:
            return element.map_attributes

        map_attributes.update(element.map_attributes)

        return map_attributes

    @classmethod
    def resolve_algo_attributes(cls, element: VisualElement, classification) -> VisualElementAttributes:
        attributes = VisualElementAttributes()
        ve_attributes = cls._ve_algo_defaults.get(classification, None)
        if ve_attributes:
            attributes.update(ve_attributes)

        if type(element) in cls._algo_defaults and classification in cls._algo_defaults[type(element)]:
            algo_defaults = cls._algo_defaults[type(element)][classification]
            attributes.update(algo_defaults)

        attributes.update(element.algo_attributes)

        return attributes


