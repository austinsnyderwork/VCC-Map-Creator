import pprint
from abc import ABC
from enum import Enum
from typing import Optional

from shared.shared_utils import Coordinate


class VisualElementAttributes:
    def __init__(self,
                 show: Optional[bool] = True,
                 facecolor: Optional[str] = None,
                 edgecolor: Optional[str] = None,
                 color: Optional[str] = None,
                 fontcolor: Optional[str] = None,
                 transparency: Optional[float] = 1.0,
                 immediately_remove: Optional[bool] = False,
                 center_view: Optional[bool] = False,
                 fontsize: Optional[float] = 10.0,
                 fontweight: Optional[str] = 'normal',
                 font: Optional[str] = None,
                 zorder: Optional[int] = 1,
                 steps_to_show: Optional[int] = 0,
                 radius: Optional[float] = None,
                 marker: Optional[str] = None,
                 label: Optional[str] = None,
                 linestyle: Optional[str] = None,
                 linewidth: Optional[float] = None,
                 size: Optional[float] = None):

        self.show = show
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.color = color
        self.fontcolor = fontcolor
        self.transparency = transparency
        self.immediately_remove = immediately_remove
        self.center_view = center_view
        self.fontsize = fontsize
        self.fontweight = fontweight
        self.font = font
        self.zorder = zorder
        self.steps_to_show = steps_to_show
        self.radius = radius
        self.marker = marker
        self.label = label
        self.linestyle = linestyle
        self.linewidth = linewidth
        self.size = size

    def update(self, new_attributes: "VisualElementAttributes"):
        for k, v in new_attributes.__dict__.items():
            if not hasattr(self, k):
                raise ValueError(f"Variable {k} not listed in {self.__class__.__name__}")


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
                 map_attributes=None,
                 algo_attributes=None,
                 classification=None,
                 **kwargs
                 ):
        self._centroid_coord = centroid_coord

        self.map_attributes = map_attributes or VisualElementAttributes()

        self.algo_attributes = algo_attributes or VisualElementAttributes()

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
                 polygon=None,
                 map_attributes: VisualElementAttributes = None,
                 algo_attributes: VisualElementAttributes = None
                 ):
        self.city_name = city_name

        self.width = width
        self.height = height

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
                 city_name: str,
                 radius: float = None,
                 polygon=None,
                 map_attributes: VisualElementAttributes = None,
                 algo_attributes: VisualElementAttributes = None,
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
                 map_attributes: VisualElementAttributes = None,
                 algo_attributes: VisualElementAttributes = None
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
                 map_attributes: VisualElementAttributes = None,
                 algo_attributes: VisualElementAttributes = None
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

