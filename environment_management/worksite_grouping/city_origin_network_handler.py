from things import entities


class CityOriginNetwork:

    def __init__(self, origin_city: entities.City, color: str):
        self.origin_city = origin_city
        self.color = color

        self.visiting_cities = set()
        self.present_origin_cities = set()

    def add_city(self, city: entities.City):
        if city.city_name in self.present_origin_cities:
            return

        self.visiting_cities.add(city)
        self.present_origin_cities.add(city.city_name)


class CityOriginNetworkHandler:

    def __init__(self, colors: list[str]):
        self.colors = colors
        self.city_origin_networks = {}

        self.colors_idx = 0

    def _get_color(self):
        color = self.colors[self.colors_idx]
        self.colors_idx += 1
        return color

    def add_city_origin_network(self, origin_city: entities.City):
        if origin_city.city_name in self.city_origin_networks:
            return

        self.city_origin_networks[origin_city.city_name] = CityOriginNetwork(origin_city=origin_city,
                                                                        color=self._get_color())

    def add_visiting_city(self, origin_city: entities.City, visiting_city: entities.City):
        self.city_origin_networks[origin_city.city_name].add_city(visiting_city)

    def get_entity_color(self, entity: entities.ProviderAssignment):
        if type(entity) is entities.ProviderAssignment:
            origin_city_name = entity.origin_city_name
            return self.city_origin_networks[origin_city_name].color

    def fill_city_origin_networks(self, entities_manager: entities.EntitiesManager):
        for provider_assignment in entities_manager.get_all_entities(entities.ProviderAssignment):
            origin_city = entities_manager.get_city(name=provider_assignment.origin_city_name)
            self.add_city_origin_network(origin_city=origin_city)

        for provider_assignment in entities_manager.get_all_entities(entities.ProviderAssignment):
            origin_city = entities_manager.get_city(name=provider_assignment.origin_city_name)
            visiting_city = entities_manager.get_city(name=provider_assignment.visiting_city_name)
            self.add_visiting_city(origin_city=origin_city,
                                   visiting_city=visiting_city)
