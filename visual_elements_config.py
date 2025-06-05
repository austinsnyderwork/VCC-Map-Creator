from dataclasses import dataclass

from visual_elements.element_classes import CityScatter, TextBoxClassification, SearchAreaClassification, \
    VisualElement, Line, SearchArea, TextBox


class DisplayEnum:
    SHOW = 'show'
    COLOR = 'color'
    TRANSPARENCY = 'transparency'
    IMMEDIATELY_REMOVE = 'immediately_remove'
    CENTER_VIEW = 'center_view'


class DisplayConfig:

    def __init__(self,
                 element_class: type(VisualElement),
                 class_type: TextBoxClassification | SearchAreaClassification = None,
                 **kwargs):
        self.attributes = kwargs

        self.element_class = element_class

        self.class_type = class_type


zorder = [CityScatter, Line, TextBox]


algo_config = {
    CityScatter: DisplayConfig(
        element_class=CityScatter,
        show=False,
        color='green',
        transparency=1.0,
        immediately_remove=False,
        center_view=False
    ),
    Line: DisplayConfig(
        element_class=Line,
        show=False,
        color='blue',
        transparency=1.0,
        immediately_remove=False,
        center_view=False
    ),
    SearchArea:
        {
            SearchAreaClassification.SCAN: DisplayConfig(
                element_class=SearchArea,
                show=True,
                color='red',
                transparency=0.5,
                immediately_remove=False,
                center_view=False
            ),
            SearchAreaClassification.FINALIST: DisplayConfig(
                element_class=SearchArea,
                class_type=SearchAreaClassification.FINALIST,
                show=True,
                color='purple',
                transparency=0.5,
                immediately_remove=True,
                center_view=False,
                steps_to_show=1
            )
        },
    TextBox: {
        TextBoxClassification.INTERSECT: DisplayConfig(
            element_class=TextBox,
            class_type=TextBoxClassification.INTERSECT,
            show=True,
            color='red',
            transparency=0.5,
            immediately_remove=False,
            center_view=False
        ),
        TextBoxClassification.BEST: DisplayConfig(
            element_class=TextBox,
            class_type=TextBoxClassification.BEST,
            show=True,
            color='black',
            transparency=0.75,
            immediately_remove=False,
            center_view=False
        ),
        TextBoxClassification.FINALIST: DisplayConfig(
            element_class=TextBox,
            class_type=TextBoxClassification.FINALIST,
            show=True,
            color='purple',
            transparency=1.0,
            immediately_remove=True,
            center_view=False,
            steps_to_show=1
        ),
        TextBoxClassification.SCAN: DisplayConfig(
            element_class=TextBox,
            class_type=TextBoxClassification.SCAN,
            show=True,
            color='blue',
            transparency=0.5,
            immediately_remove=True,
            center_view=False,
            steps_to_show=5
        ),
        TextBoxClassification.INVALID: DisplayConfig(
            element_class=TextBox,
            class_type=TextBoxClassification.INVALID,
            show=True,
            color='gray',
            transparency=0.5,
            immediately_remove=False,
            center_view=False
        )
    }
}

