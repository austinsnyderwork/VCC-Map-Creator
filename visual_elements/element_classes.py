
from abc import ABC
from enum import Enum

from shared.shared_utils import Coordinate


class VisualElement(ABC):

    _algo_defaults = dict()

    def __init__(self,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None,
                 classification = None,
                 **kwargs
                 ):
        self.polygon = polygon

        self.map_attributes = map_attributes or dict()
        self.algorithm_attributes = algorithm_attributes or dict()
        self.classification = classification
        
        a = self.algorithm_attributes
        for default_k, default_v in self.__class__._algo_defaults.items():
            a[default_k] = a[default_k] if default_k in a else default_v

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "_algo_defaults"):
            raise ValueError(f"Subclass of {cls.__name__} must define _algo_defaults")

    @classmethod
    def _apply_attributes(cls, attributes: dict):
        for k, v in attributes.items():
            if not hasattr(cls, k):
                setattr(cls, k, v)

    @classmethod
    def _fill_default(cls):
        classification = getattr(cls, "classification", None)

        if classification and classification in cls._algo_defaults:
            classification_attributes = cls._algo_defaults[classification]
            cls._apply_attributes(classification_attributes)

        # Classification-specific attributes take priority over general attributes
        general_attributes = {k: v for k, v in cls._algo_defaults.items() if isinstance(k, str)}
        cls._apply_attributes(general_attributes)



class TextBoxClassification(Enum):
    BEST = "best"
    FINALIST = "finalist"
    INTERSECT = "intersect"
    SCAN = "scan_box"
    INVALID = "invalid"


class TextBoxAttribute(Enum):
    FONT_SIZE = "font_size"
    FONT = "font"


class TextBox(VisualElement):

    _algo_defaults = {
        TextBoxClassification.INTERSECT: {
            "show": True,
            "color": "red",
            "transparency": 0.5,
            "immediately_remove": False,
            "center_view": False
        },
        TextBoxClassification.BEST: {
            "show": True,
            "color": "black",
            "transparency": 0.75,
            "immediately_remove": False,
            "center_view": False
        },
        TextBoxClassification.FINALIST: {
            "show": True,
            "color": "purple",
            "transparency": 1.0,
            "immediately_remove": True,
            "center_view": False,
            "steps_to_show": 1
        },
        TextBoxClassification.SCAN: {
            "show": True,
            "color": "blue",
            "transparency": 0.5,
            "immediately_remove": True,
            "center_view": False,
            "steps_to_show": 5
        },
        TextBoxClassification.INVALID: {
            "show": True,
            "color": "gray",
            "transparency": 0.5,
            "immediately_remove": False,
            "center_view": False
        }
    }

    def __init__(self,
                 city_name: str,
                 centroid: Coordinate = None,
                 width: float = None,
                 height: float = None,
                 classification: TextBoxClassification = None,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        self.city_name = city_name

        self.centroid = centroid
        self.width = width
        self.height = height
        self.classification = classification

        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)


class ScatterAttributes(Enum):
    RADIUS = "radius"
    COLOR = "color"
    OUTER_COLOR = "outer_color"
    MARKER = "marker"


class CityScatter(VisualElement):

    _defaults = {
        "show": False,
        "color": "blue",
        "transparency": 1.0,
        "immediately_remove": False,
        "center_view": False
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
            "center_view": False
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


class LineAttributes(Enum):
    COLOR = "color"


class Line(VisualElement):
    
    _algo_defaults = {
        "show": False,
        "color": "blue",
        "transparency": 1.0,
        "immediately_remove": False,
        "center_view": False
    }
    
    def __init__(self,
                 origin_coordinate: Coordinate,
                 visiting_coordinate: Coordinate,
                 width: float,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)

        self.origin_coordinate = origin_coordinate
        self.visiting_coordinate = visiting_coordinate
        self.width = width


