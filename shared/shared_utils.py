from enum import Enum


class Coordinate:

    def __init__(self, longitude: float, latitude: float):
        self.lon = longitude
        self.lat = latitude

    def __hash__(self):
        return hash((self.lon, self.lat))

    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return False

        return self.lon == other.lon and self.lat == other.lat


class Direction(Enum):
    UP = 'up'
    DOWN = 'down'
    LEFT = 'left'
    RIGHT = 'right'


class CityClassification(Enum):
    ORIGIN = 'origin_city'
    VISITING = 'visiting_city'
    DUAL = 'dual_city'
