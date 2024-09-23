from .provider import Provider


class VccClinicSite:

    def __init__(self, name: str, city_name: str, city_coord: tuple):
        self.name = name
        self.city_name = city_name
        self.city_coord = city_coord

        self.providers_leaving = set()
        self.providers_visiting = set()

    def add_provider(self, provider: Provider, direction: str):
        direction_lists = {
            'visiting': self.providers_visiting,
            'leaving': self.providers_leaving
        }
        if provider not in direction_lists.keys():
            raise ValueError(f"Passed in direction '{direction}' is not one of acceptable directions "
                             f"{list(direction_lists.keys())}")

        direction_lists[direction].add(provider)
