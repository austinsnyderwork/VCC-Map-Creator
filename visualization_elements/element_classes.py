
from abc import ABC
from enum import Enum


class VisualizationElement(ABC):

    def __init__(self,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        self.polygon = polygon

        self.map_attributes = map_attributes or dict()
        self.algorithm_attributes = algorithm_attributes or dict()


class TextBoxClassification(Enum):
    BEST = 'best'
    FINALIST = 'finalist'
    INTERSECT = 'intersect'
    SCAN = 'scan_box'
    INVALID = 'invalid'


class TextBox(VisualizationElement):

    def __init__(self,
                 classification: TextBoxClassification,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)

        self.classification = classification


class ScatterAttributes(Enum):
    RADIUS = 'radius'
    COLOR = 'color'


class CityScatter(VisualizationElement):

    def __init__(self,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)


class SearchAreaClassification(Enum):
    SCAN = 'scan_area'
    FINALIST = 'finalist_area'


class SearchArea(VisualizationElement):

    def __init__(self,
                 classification: SearchAreaClassification,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)

        self.classification = classification


class Line(VisualizationElement):

    def __init__(self,
                 polygon=None,
                 map_attributes: dict = None,
                 algorithm_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algorithm_attributes=algorithm_attributes)


