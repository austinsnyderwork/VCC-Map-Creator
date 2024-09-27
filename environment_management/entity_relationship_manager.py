from things import entities


class EntityRelationshipManager:

    def __init__(self, cities: list[entities.City], clinics: list[entities.VccClinicSite],
                  provider_assignment: list[entities.ProviderAssignment]):
        self.cities = cities
        self.clinics = clinics
        self.provider_assignment = provider_assignment

def _fill_cities_with_clinics(cities: list[entities.City], clinics: list[entities.VccClinicSite]):
    cities_dict = {}
    for city in cities:
        cities_dict[city.name] = city

    for clinic in clinics:


def _fill_clinics_with_provider_assignments()


def fill_entities(cities: list[entities.City], clinics: list[entities.VccClinicSite],
                  provider_assignment: list[entities.ProviderAssignment]):




