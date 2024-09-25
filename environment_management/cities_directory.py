from things.entities import entities


class CitiesDirectory:

    def __init__(self):
        self._cities = {}

    def add_city(self, city: entities.City):
        if city.name not in self._cities:
            self._cities[city.name] = city

    def get_city(self, name: str):
        return self._cities[name]
