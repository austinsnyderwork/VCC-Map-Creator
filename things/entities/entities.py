
class Entity:
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

    def add_provider(self, provider: Provider, specialty: str, direction: str):
        direction_lists = {
            'visiting': self.leaving_provider_assignments,
            'leaving': self.visiting_provider_assignments
        }
        if provider not in direction_lists.keys():
            raise ValueError(f"Passed in direction '{direction}' is not one of acceptable directions "
                             f"{list(direction_lists.keys())}")

        provider_assignment = ProviderAssignment(provider=provider, specialty=specialty)
        direction_lists[direction].add(provider_assignment)

    @property
    def visiting_specialties(self):
        specialties = (provider_assignment.specialty for provider_assignment in self.visiting_provider_assignments)
        return specialties


class City(Entity):

    def __init__(self, name: str, coord: tuple):
        self.name = name
        self.coord = coord

        self.visiting_clinics = set()
        self.leaving_clinics = set()

        self.visiting_providers = set()
        self.leaving_providers = set()

        self._visiting_specialties = set()
        self.leaving_specialties = set()

        self.data_is_static = False

    def add_clinic_site(self, clinic_site: VccClinicSite, direction: str):
        directions_lists = {
            'visiting': self.visiting_clinics,
            'leaving': self.leaving_clinics
        }

        providers_lists = {
            'visiting': (self.visiting_providers, clinic_site.providers_visiting),
            'leaving': (self.leaving_providers, clinic_site.providers_leaving)
        }
        if direction not in directions_lists.keys():
            raise ValueError(f"add_clinic_site direction value '{direction}' is not one of acceptable directions: "
                             f"{list(directions_lists.keys())}")

        directions_lists[direction].add(clinic_site)

        self_providers, clinic_providers = providers_lists[direction]
        self_providers.update(clinic_providers)
        self.data_is_static = False

    @property
    def visiting_specialties(self):
        if self.data_is_static and self.visiting_specialties:
            return self._visiting_specialties

        self._visiting_specialties = set()
        for clinic in self.visiting_clinics:
            self._visiting_specialties.update(clinic.visiting_specialties)

        self.data_is_static = True

    @property
    def site_type(self):
        if len(self.visiting_clinics) > 0 and len(self.leaving_clinics) > 0:
            return 'dual_origin_visiting'
        elif len(self.visiting_clinics) > 0:
            return 'visiting'
        else:
            return 'origin'

