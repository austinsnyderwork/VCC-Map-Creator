from .city_origin_network import CityOriginNetwork
import visualization_elements


class CityOriginNetwork:

    def __init__(self, origin_city: visualization_elements.City, color: str):
        self.origin_city = origin_city
        self.color = color

        self.outpatient_cities = set()
        self.present_origin_cities = set()

    def add_city(self, city: visualization_elements.City):
        if city.name in self.present_origin_cities:
            return

        self.outpatient_cities.add(city)
        self.present_origin_cities.add(city.name)


class CityOriginNetworkHandler:

    def __init__(self, colors: list[str]):
        self.colors = colors
        self.city_origin_networks = {}
        self._dual_origin_outpatient = []

        self.colors_idx = 0

    def _get_color(self):
        color = self.colors[self.colors_idx]
        self.colors_idx += 1
        return color

    def add_city_origin_network(self, origin_city: visualization_elements.City):
        if origin_city.name in self.city_origin_networks:
            return

        self.city_origin_networks[origin_city.name] = CityOriginNetwork(origin_city=origin_city,
                                                                        color=self._get_color())

    @property
    def dual_origin_outpatient(self) -> list[visualization_elements.City]:
        if len(self.city_origin_networks) == 0:
            raise ValueError(f"Attempted to access dual_origin_outpatient before city_origin_networks is created.")

        if self._dual_origin_outpatient:
            return self.dual_origin_outpatient

        for city_origin_network in self.city_origin_networks.values():
            for outpatient_city in city_origin_network.outpatients:
                if outpatient_city.name in self.city_origin_networks.keys():
                    self._dual_origin_outpatient.append(outpatient_city)

        return self._dual_origin_outpatient


