
class City:

    def __init__(self, name: str, coord: tuple):
        self.name = name
        self.coord = coord


class CitiesDirectory:

    def __init__(self):
        self._cities = {}

    def add_city(self, name: str, coord: tuple):
        if name not in self._cities:
            new_city = City(name=name, coord=coord)
            self._cities[new_city.name] = new_city

    def get_city(self, name: str):
        return self._cities[name]
