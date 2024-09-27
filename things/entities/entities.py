from abc import ABC


class Entity(ABC):
    pass


class Provider(Entity):

    def __init__(self, name: str):
        self.name = name


class ProviderAssignment:

    def __init__(self, provider: Provider, specialty: str, origin_site: 'VccClinicSite', visiting_site: 'VccClinicSite'):
        self.provider = provider
        self.specialty = specialty
        self.origin_site = origin_site,
        self.visiting_site = visiting_site


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


class City(Entity):

    def __init__(self, name: str, coord: tuple):
        self.name = name
        self.coord = coord

        self.clinics = {
            'visiting': set(),
            'leaving': set()
        }

        self.data_is_static = False

    def add_clinic_site(self, clinic_site: VccClinicSite, direction: str):
        if direction not in self.clinics.keys():
            raise ValueError(f"add_clinic_site direction value '{direction}' is not one of acceptable directions: "
                             f"{list(self.clinics.keys())}")

        self.clinics[direction].add(clinic_site)

        self.data_is_static = False

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

