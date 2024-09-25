
class Entity:
    pass


class Provider(Entity):

    def __init__(self, name: str):
        self.name = name


class ProviderAssignment:

    def __init__(self, provider: Provider, specialty: str):
        self.provider = provider
        self.specialty = specialty


class VccClinicSite(Entity):

    def __init__(self, name: str, city_name: str, city_coord: tuple):
        self.name = name
        self.city_name = city_name
        self.city_coord = city_coord

        self.providers_leaving = set()
        self.providers_visiting = set()

    def add_provider(self, provider: Provider, specialty: str, direction: str):
        direction_lists = {
            'visiting': self.providers_visiting,
            'leaving': self.providers_leaving
        }
        if provider not in direction_lists.keys():
            raise ValueError(f"Passed in direction '{direction}' is not one of acceptable directions "
                             f"{list(direction_lists.keys())}")

        provider_assignment = ProviderAssignment(provider=provider, specialty=specialty)
        direction_lists[direction].add(provider_assignment)


class City(Entity):

    def __init__(self, name: str, coord: tuple):
        self.name = name
        self.coord = coord

        self.visiting_clinic_sites = set()
        self.leaving_clinic_sites = set()

        self.visiting_providers = set()
        self.leaving_providers = set()

    def add_clinic_site(self, clinic_site: VccClinicSite, direction: str):
        directions_lists = {
            'visiting': self.visiting_clinic_sites,
            'leaving': self.leaving_clinic_sites
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

    @property
    def origin_and_outpatient(self):
        return len(self.visiting_clinic_sites) > 0 and len(self.leaving_clinic_sites) > 0

