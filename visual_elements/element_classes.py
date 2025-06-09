
from abc import ABC
from enum import Enum

from shared.shared_utils import Coordinate


class VisualElement(ABC):

    def __init__(self,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None,
                 classification=None,
                 **kwargs
                 ):
        self.map_attributes = map_attributes or dict()
        self.algorithm_attributes = algorithm_attributes or dict()

        self._set_attributes(
            default_attributes=self.__class__._algo_defaults,
            attributes_variable=self.algorithm_attributes
        )
        self._set_attributes(
            default_attributes=self.__class__._map_defaults,
            attributes_variable=self.map_attributes
        )
        self.polygon = polygon

        self.classification = classification

        for k, v in kwargs.items():
            setattr(self, k, v)

    def _set_attributes(self, default_attributes: dict, attributes_variable: dict):
        if hasattr(self, 'classification'):
            # Set the classification-specific default attributes first
            for default_k, default_v in default_attributes.items():
                if self.classification == default_k:
                    for k, v in default_v.items():
                        if k not in attributes_variable:
                            attributes_variable[k] = v

        # Set the VisualElement type default attributes next
        for default_k, default_v in default_attributes.items():
            if isinstance(default_k, str):
                if default_k not in attributes_variable:
                    attributes_variable[default_k] = default_v

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "_algo_defaults"):
            raise ValueError(f"Subclass of {cls.__name__} must define _algo_defaults.")
        elif not hasattr(cls, "_map_defaults"):
            raise ValueError(f"Subclass of {cls.__name__} must define _map_defaults.")


class TextBoxClassification(Enum):
    BEST = "best"
    FINALIST = "finalist"
    INTERSECT = "intersect"
    SCAN = "scan_box"
    INVALID = "invalid"


class TextBox(VisualElement):

    _algo_defaults = {
        TextBoxClassification.INTERSECT: {
            "show": True,
            "facecolor": "red",
            "transparency": 0.5,
            "immediately_remove": True,
            "center_view": False
        },
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
        },
        TextBoxClassification.INVALID: {
            "show": True,
            "facecolor": "gray",
            "transparency": 0.5,
            "immediately_remove": False,
            "center_view": False
        }
    }

    _map_defaults = {
        "fontsize": 10,
        "font": "Roboto",
        "zorder": 2
    }

    def __init__(self,
                 city_name: str = None,
                 centroid: Coordinate = None,
                 width: float = None,
                 height: float = None,
                 classification: TextBoxClassification = None,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        self.city_name = city_name

        self._centroid = centroid
        self.width = width
        self.height = height
        self.classification = classification

        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)

    @property
    def centroid(self):
        if self._centroid:
            return self._centroid

        return Coordinate(
            longitude=self.polygon.centroid.x,
            latitude=self.polygon.centroid.y
        )



class CityScatter(VisualElement):

    _algo_defaults = {
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

    _map_defaults = {
        "zorder": 3
    }

    def __init__(self,
                 centroid: Coordinate,
                 radius: float,
                 city_name: str,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None,
                 **kwargs
                 ):

        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes,
                         **kwargs)

        self.centroid = centroid
        self.radius = radius
        self.city_name = city_name


class SearchAreaClassification(Enum):
    SCAN = "scan_area"
    FINALIST = "finalist_area"


class SearchArea(VisualElement):

    _algo_defaults = {
        SearchAreaClassification.SCAN: {
            "show": True,
            "color": "red",
            "transparency": 0.5,
            "immediately_remove": False,
            "center_view": True
        },
        SearchAreaClassification.FINALIST: {
            "class_type": SearchAreaClassification.FINALIST,
            "show": True,
            "color": "purple",
            "transparency": 0.5,
            "immediately_remove": True,
            "center_view": False,
            "steps_to_show": 1
        }
    }

    _map_defaults = {}

    def __init__(self,
                 classification: SearchAreaClassification,
                 centroid: Coordinate,
                 width: float,
                 height: float,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)

        self.centroid = centroid
        self.width = width
        self.height = height
        self.classification = classification


class Line(VisualElement):
    
    _algo_defaults = {
        "show": False,
        "color": "blue",
        "transparency": 1.0,
        "immediately_remove": False,
        "center_view": False,
        "linestyle": "-",
        "linewidth": 0.1,
        "zorder": 1
    }

    _map_defaults = {
        "zorder": 1
    }
    
    def __init__(self,
                 origin_coordinate: Coordinate,
                 visiting_coordinate: Coordinate,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)

        self.origin_coordinate = origin_coordinate
        self.visiting_coordinate = visiting_coordinate

    @property
    def x_data(self):
        return self.origin_coordinate.lon, self.visiting_coordinate.lon

    @property
    def y_data(self):
        return self.origin_coordinate.lat, self.visiting_coordinate.lat

