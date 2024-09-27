from abc import ABC


class Entity(ABC):
    pass


class Provider(Entity):

    def __init__(self, name: str):
        self.name = name


class ProviderAssignment:

    def __init__(self, provider: Provider, specialty: str, origin_site_name: str, origin_city_name: str,
                 visiting_site_name: str, visiting_city_name: str):
        self.provider = provider
        self.specialty = specialty
        self.origin_site_name = origin_site_name
        self.origin_city_name = origin_city_name
        self.visiting_site_name = visiting_site_name
        self.visiting_city_name = visiting_city_name


class VccClinicSite(Entity):

    def __init__(self, name: str, city_name: str, city_coord: tuple):
        self.name = name
        self.city_name = city_name
        self.city_coord = city_coord

        self.leaving_provider_assignments = set()
        self.visiting_provider_assignments = set()

    def add_provider_assignment(self, provider_assignment: ProviderAssignment, direction: str):
        direction_lists = {
            'visiting': self.leaving_provider_assignments,
            'leaving': self.visiting_provider_assignments
        }
        if direction not in direction_lists.keys():
            raise ValueError(f"Passed in direction '{direction}' is not one of acceptable directions "
                             f"{list(direction_lists.keys())}")
        direction_lists[direction].add(provider_assignment)

    @property
    def visiting_specialties(self):
        specialties = (provider_assignment.specialty for provider_assignment in self.visiting_provider_assignments)
        return specialties

    @property
    def visiting_cities(self):
        visiting_cities = set()
        for provider_assignment in self.visiting_provider_assignments:
            visiting_cities.add(provider_assignment.visiting_city_name)
        return visiting_cities

    @property
    def leaving_cities(self):
        leaving_cities = set()
        for provider_assignment in self.leaving_provider_assignments:
            leaving_cities.add(provider_assignment.origin_city_name)
        return leaving_cities


class City(Entity):

    def __init__(self, name: str, coord: tuple):
        self.name = name
        self.coord = coord

        self.clinics = {
            'visiting': set(),
            'leaving': set()
        }

    def add_clinic_site(self, clinic_site: VccClinicSite, direction: str):
        if direction not in self.clinics.keys():
            raise ValueError(f"add_clinic_site direction value '{direction}' is not one of acceptable directions: "
                             f"{list(self.clinics.keys())}")

        self.clinics[direction].add(clinic_site)

    @property
    def site_type(self):
        if len(self.clinics['visiting']) > 0 and len(self.clinics['leaving']) > 0:
            return 'dual_origin_visiting'
        elif len(self.clinics['leaving']) > 0:
            return 'visiting'
        elif len(self.clinics['visiting']):
            return 'origin'
        else:
            raise RuntimeError(f"Attempted to define site type for city '{self.name}' without any visiting or leaving "
                               f"clinics.")

