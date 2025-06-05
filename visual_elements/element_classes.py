
from abc import ABC
from enum import Enum

from shared.shared_utils import Coordinate


class VisualElement(ABC):

    def __init__(self,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None,
                 **kwargs
                 ):
        self.polygon = polygon

        self.map_attributes = map_attributes or dict()
        self.algorithm_attributes = algorithm_attributes or dict()

        for k, v in kwargs.items():
            setattr(self, k, v)


class TextBoxClassification(Enum):
    BEST = 'best'
    FINALIST = 'finalist'
    INTERSECT = 'intersect'
    SCAN = 'scan_box'
    INVALID = 'invalid'


class TextBox(VisualElement):

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
    RADIUS = 'radius'
    COLOR = 'color'
    OUTER_COLOR = 'outer_color'
    MARKER = 'marker'


class CityScatter(VisualElement):

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
    SCAN = 'scan_area'
    FINALIST = 'finalist_area'


class SearchArea(VisualElement):

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
    COLOR = 'color'


class Line(VisualElement):

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


