import logging

import entities


class CityOriginNetwork:

    def __init__(self, origin_city: entities.City, color: str):
        self.origin_city = origin_city
        self.color = color

        self.outpatient_cities = set()
        self.present_origin_cities = set()

    def add_city(self, city: entities.City):
        if city.name in self.present_origin_cities:
            return

        self.outpatient_cities.add(city)
        self.present_origin_cities.add(city.name)
