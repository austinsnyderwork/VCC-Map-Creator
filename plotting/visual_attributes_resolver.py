from visual_elements.element_classes import VisualElementClassification, TextBoxClassification, VisualElement, CityScatter, SearchArea, Line, TextBox


class VisualElementAttributesResolver:

    _ve_algo_defaults = {
        VisualElementClassification.INTERSECT: {
            "show": True,
            "facecolor": "black",
            "transparency": 0.5,
            "immediately_remove": True,
            "center_view": False
        }
    }

    _algo_defaults = {
        TextBox: {
            TextBoxClassification.BEST: {
                "show": True,
                "facecolor": "black",
                "transparency": 0.75,
                "immediately_remove": False,
                "center_view": False,
                "zorder": 2
            },
            TextBoxClassification.FINALIST: {
                "show": True,
                "facecolor": "purple",
                "transparency": 1.0,
                "immediately_remove": True,
                "center_view": False,
                "steps_to_show": 1
            },
            TextBoxClassification.SCAN: {
                "show": True,
                "facecolor": "blue",
                "transparency": 0.5,
                "immediately_remove": True,
                "center_view": False,
                "steps_to_show": 5
            }
        },
        CityScatter: {
            None: {
                "show": False,
                "facecolor": "blue",
                "edgecolor": "blue",
                "transparency": 1.0,
                "immediately_remove": False,
                "center_view": False,
                "marker": "o",
                "zorder": 3,
                "label": "algo_label"
            }
        },
        SearchArea: {
            None: {
                "show": True,
                "color": "purple",
                "transparency": 0.5,
                "immediately_remove": True,
                "center_view": False,
                "steps_to_show": 1
            }
        },
        Line: {
            None: {
                "show": False,
                "color": "blue",
                "transparency": 1.0,
                "immediately_remove": False,
                "center_view": False,
                "linestyle": "-",
                "linewidth": 0.1,
                "zorder": 1
            }
        }
    }

    _map_defaults = {
        TextBox: {
            "fontsize": 10,
            "font": "Roboto",
            "fontweight": "normal",
            "zorder": 1
        },
        Line: {
            "zorder": 0
        },
        CityScatter: {
            "zorder": 2
        }
    }

    @classmethod
    def resolve_map_attributes(cls, element: VisualElement) -> dict:
        map_attributes = cls._map_defaults.get(type(element), {})
        map_attributes.update(element.map_attributes)

        return map_attributes

    @classmethod
    def resolve_algo_attributes(cls, element: VisualElement, classification) -> dict:
        algo_attributes = cls._ve_algo_defaults.get(classification, {})
        algo_defaults = cls._algo_defaults.get(type(element), {}).get(classification, {})

        algo_attributes.update(algo_defaults)

        algo_attributes.update(element.algo_attributes)

        return algo_attributes


