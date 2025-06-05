from dataclasses import dataclass

from visual_elements.element_classes import CityScatter, TextBoxClassification, SearchAreaClassification, \
    VisualElement, Line, SearchArea, TextBox


class DisplayEnum:
    SHOW = 'show'
    COLOR = 'color'
    TRANSPARENCY = 'transparency'
    IMMEDIATELY_REMOVE = 'immediately_remove'
    CENTER_VIEW = 'center_view'


@dataclass
class DisplayConfig:
    element_class: type(VisualElement)
    show: bool
    color: str
    transparency: float
    immediately_remove: bool
    center_view: bool

    steps_to_show: int = None
    class_type: TextBoxClassification | SearchAreaClassification = None

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
[algo_display.nearby]
show = True
color = gray
transparency = 0.5
immediately_remove = False
center_view = False

[map_display]
show_display = False

linewidth = 2
scatter_size = 70

scatter_zorder = 2
best_poly_zorder = 3
line_zorder = 1

[map_display.origin_city]
color = red
outer_color = red
marker = s

[map_display.visiting_city]
color = blue
outer_color = blue
marker = o

[map_display.dual_city]
color = blue
outer_color = red
marker = s

[map_display.text]
font = Tahoma
fontsize = 12
fontweight = semibold
font_color = black

[num_visiting_providers.range_1]
min = 1
max = 2
color = blue
edgecolor = blue
scatter_size = 25
marker = o
label = 5-10

[num_visting_providers.range_2]
min = 2
max = 5
color = red
edgecolor = red
scatter_size = 50
marker = o
label = 11-15

[num_visting_providers.range_3]
min = 16
max = 20
color = yellow
edgecolor = yellow
scatter_size = 75
marker = o
label = 16-20

[num_visiting_providers.range_4]
min = 20
color = green
edgecolor = green
scatter_size = 100
marker = o
label = 20+

