from .vcc_clinic_site import VccClinicSite


class City:

    def __init__(self, name: str, coord: tuple):
        self.name = name
        self.coord = coord

        self.visiting_clinic_sites = set()
        self.leaving_clinic_sites = set()

    def add_clinic_site(self, clinic_site: VccClinicSite, direction: str):
        directions_lists = {
            'visiting': self.visiting_clinic_sites,
            'leaving': self.leaving_clinic_sites
        }
        if direction not in directions_lists.keys():
            raise ValueError(f"add_clinic_site direction value '{direction}' is not one of acceptable directions: "
                             f"{list(directions_lists.keys())}")

        directions_lists[direction].add(clinic_site)


class CitiesDirectory:

    def __init__(self):
        self._cities = {}

    def add_city(self, city: City):
        if city.name not in self._cities:
            self._cities[city.name] = city

    def get_city(self, name: str):
        return self._cities[name]
