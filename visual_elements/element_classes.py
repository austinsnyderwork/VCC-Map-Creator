import pprint
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from shared.shared_utils import Coordinate


class VisualElementAttributes:
    def __init__(self,
                 show: Optional[bool] = None,
                 facecolor: Optional[str] = None,
                 edgecolor: Optional[str] = None,
                 transparency: Optional[float] = None,
                 immediately_remove: Optional[bool] = None,
                 center_view: Optional[bool] = None,
                 zorder: Optional[int] = None,
                 steps_to_show: Optional[int] = None):
        self._explicitly_set = set()

        self.show = show
        if show is not None: self._explicitly_set.add("show")

        self.facecolor = facecolor
        if facecolor is not None: self._explicitly_set.add("facecolor")

        self.edgecolor = edgecolor
        if edgecolor is not None: self._explicitly_set.add("edgecolor")

        self.transparency = transparency
        if transparency is not None: self._explicitly_set.add("transparency")

        self.immediately_remove = immediately_remove
        if immediately_remove is not None: self._explicitly_set.add("immediately_remove")

        self.center_view = center_view
        if center_view is not None: self._explicitly_set.add("center_view")

        self.zorder = zorder
        if zorder is not None: self._explicitly_set.add("zorder")

        self.steps_to_show = steps_to_show
        if steps_to_show is not None: self._explicitly_set.add("steps_to_show")

    def fetch_attributes(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k in self._explicitly_set}

    def update(self, new_attributes: "VisualElementAttributes"):
        new_atts = new_attributes.fetch_attributes()
        for k, v in new_atts.items():
            if not hasattr(self, k):
                raise ValueError(f"Variable {k} not listed in {self.__class__.__name__}")
            setattr(self, k, v)
            self._explicitly_set.add(k)


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


class VisualElement(ABC):

    def __init__(self,
                 centroid_coord: Coordinate = None,
                 polygon=None,
                 map_attributes=None,
                 algo_attributes=None,
                 classification=None,
                 **kwargs
                 ):
        self.centroid_coord = centroid_coord

        self.map_attributes = map_attributes or VisualElementAttributes()
        self.algo_attributes = algo_attributes or VisualElementAttributes()

        self.polygon = polygon

        self.classification = classification

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    @abstractmethod
    def _key(self):
        pass

    def __hash__(self):
        return hash(self._key)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self._key == other._key

    @abstractmethod
    def __str__(self):
        pass


class AlgorithmClassification(Enum):
    TEXT_FINALIST = "finalist"
    TEXT_SCAN = "scan_box"
    TEXT_BEST = "best"
    INTERSECT = "intersect"
    LINE = 'line'
    CITY_SCATTER = 'scatter'


class TextBox(VisualElement):

    def __init__(self,
                 font: str,
                 fontsize: int,
                 fontweight: str,
                 fontcolor: str,
                 zorder: int,
                 centroid_coord: Coordinate,
                 city_name: str = None,
                 width: float = None,
                 height: float = None,
                 polygon=None,
                 map_attributes: VisualElementAttributes = None,
                 algo_attributes: VisualElementAttributes = None
                 ):
        self.font = font
        self.fontsize = fontsize
        self.fontweight = fontweight
        self.fontcolor = fontcolor
        self.zorder = zorder
        self.city_name = city_name

        self.width = width
        self.height = height

        super().__init__(centroid_coord=centroid_coord,
                         polygon=polygon,
                         map_attributes=map_attributes,
                         algo_attributes=algo_attributes)

    @property
    def _key(self):
        return self.city_name, self.centroid_coord

    def __str__(self):
        return f"{self.__class__.__name__}:{self.city_name}"

    @property
    def bounds(self):
        return self.polygon.bounds


class CityScatter(VisualElement):

    def __init__(self,
                 coord: Coordinate,
                 city_name: str,
                 radius: int,
                 marker: str,
                 facecolor: str,
                 edgecolor: str,
                 label: str = None,
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
        self.marker = marker
        self.facecolor = facecolor
        self.edgecolor = edgecolor
        self.label = label

    @property
    def _key(self):
        return self.city_name, self.centroid_coord

    def __str__(self):
        return f"{self.__class__.__name__}:{self.city_name}"


class Line(VisualElement):

    def __init__(self,
                 origin_city: str,
                 visiting_city: str,
                 origin_coordinate: Coordinate,
                 visiting_coordinate: Coordinate,
                 linewidth: int,
                 linestyle: str,
                 facecolor: str,
                 zorder: int,
                 map_attributes: VisualElementAttributes = None,
                 polygon=None,
                 algo_attributes: VisualElementAttributes = None
                 ):
        super().__init__(polygon=polygon,
                         map_attributes=map_attributes,
                         algo_attributes=algo_attributes)
        self.origin_city = origin_city
        self.visiting_city = visiting_city

        self.linewidth = linewidth
        self.linestyle = linestyle
        self.facecolor = facecolor
        self.zorder = zorder
        self.origin_coordinate = origin_coordinate
        self.visiting_coordinate = visiting_coordinate

    @property
    def _key(self):
        return self.origin_city, self.origin_coordinate.lon_lat, self.visiting_city, self.visiting_coordinate.lon_lat

    def __str__(self):
        return f"{self.__class__.__name__}:{self.origin_city}->{self.visiting_city}"

    @property
    def x_data(self):
        return self.origin_coordinate.lon, self.visiting_coordinate.lon

    @property
    def y_data(self):
        return self.origin_coordinate.lat, self.visiting_coordinate.lat
