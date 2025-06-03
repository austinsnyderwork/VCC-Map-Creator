

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
