import pprint
from abc import ABC
from enum import Enum

from shared.shared_utils import Coordinate


def _find_class_key(search_key, data: dict):
    # If all the keys are strings then there's no class to find
    if all([isinstance(k, str) for k in data]):
        return None

    for inner_k, inner_v in data.items():
        if inner_k == search_key and isinstance(inner_v, dict):
            print(f"Key {search_key} data:\n{pprint.pformat(inner_v)}")
            return inner_v
        if isinstance(inner_v, dict):
            # This function only looks for class keys. If all the keys are strings then there's nothing to find
            if all([isinstance(k2, str) for k2, v2 in inner_v.items()]):
                continue

            found = _find_class_key(search_key, inner_v)
            if found is not None:
                print(f"Key {search_key} data:\n{pprint.pformat(found)}")
                return found
    print(f"No data for {search_key}")
    return None


class VisualElementClassification(Enum):
    INTERSECT = 'intersect'


class VisualElement(ABC):

    def __init__(self,
                 centroid_coord: Coordinate = None,
                 polygon=None,
                 map_attributes: dict = None,
                 algo_attributes: dict = None,
                 classification=None,
                 **kwargs
                 ):
        self._centroid_coord = centroid_coord

        self.map_attributes = map_attributes or dict()

        self.algo_attributes = algo_attributes or dict()

        self.polygon = polygon

        self.classification = classification

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def centroid_coord(self):
        if self._centroid_coord:
            return self._centroid_coord
        else:
            return Coordinate(
                longitude=self.polygon.centroid.x,
                latitude=self.polygon.centroid.y
            )


class TextBoxClassification(Enum):
    BEST = "best"
    FINALIST = "finalist"
    SCAN = "scan_box"
    INVALID = "invalid"


class TextBox(VisualElement):

    def __init__(self,
                 centroid_coord: Coordinate = None,
                 city_name: str = None,
                 width: float = None,
                 height: float = None,
                 classification: TextBoxClassification = None,
                 polygon=None,
                 map_attributes: dict = None,
                 algo_attributes: dict = None
                 ):
        self.city_name = city_name

        self.width = width
        self.height = height
        self.classification = classification

        super().__init__(centroid_coord=centroid_coord,
                         polygon=polygon,
                         map_attributes=map_attributes,
                         algo_attributes=algo_attributes)

    @property
    def bounds(self):
        return self.polygon.bounds


class CityScatter(VisualElement):

    def __init__(self,
                 coord: Coordinate,
                 radius: float,
                 city_name: str,
                 polygon=None,
                 map_attributes: dict = None,
                 algo_attributes: dict = None,
                 **kwargs
                 ):

        super().__init__(centroid_coord=coord,
                         polygon=polygon,
                         map_attributes=map_attributes,
                         algo_attributes=algo_attributes,
                         **kwargs)

        self.coord = coord
        self.radius = radius
        self.city_name = city_name


class SearchArea(VisualElement):

    def __init__(self,
                 centroid: Coordinate,
                 width: float,
                 height: float,
                 polygon=None,
                 map_attributes: dict = None,
                 algo_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algo_attributes=algo_attributes)

        self.centroid = centroid
        self.width = width
        self.height = height


class Line(VisualElement):
    
    def __init__(self,
                 origin_coordinate: Coordinate,
                 visiting_coordinate: Coordinate,
                 polygon=None,
                 map_attributes: dict = None,
                 algo_attributes: dict = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algo_attributes=algo_attributes)

        self.origin_coordinate = origin_coordinate
        self.visiting_coordinate = visiting_coordinate

    @property
    def x_data(self):
        return self.origin_coordinate.lon, self.visiting_coordinate.lon

    @property
    def y_data(self):
        return self.origin_coordinate.lat, self.visiting_coordinate.lat

