from things import entities


class EntityRelationshipManager:

    def __init__(self, cities: list[entities.City], clinics: list[entities.VccClinicSite],
                 provider_assignments: list[entities.ProviderAssignment]):
        self.cities = cities
        self.clinics = clinics
        self.provider_assignments = provider_assignments

    def fill_entities(self):
        self._fill_clinics_with_provider_assignments()
        self._fill_cities_with_clinics()

    def _fill_clinics_with_provider_assignments(self):
        clinics_dict = {}
        for clinic in self.clinics:
            clinics_dict[clinic.site_name] = clinic

        for provider_assignment in self.provider_assignments:
            origin_site = clinics_dict[provider_assignment.origin_site_name]
            visiting_site = clinics_dict[provider_assignment.visiting_site_name]

            origin_site.leaving_provider_assignments.add(provider_assignment)
            visiting_site.visiting_provider_assignments.add(provider_assignment)

    def _fill_cities_with_clinics(self):
        cities_dict = {}
        for city in self.cities:
            cities_dict[city.city_name] = city

        for clinic in self.clinics:
            for visiting_city_name in clinic.visiting_cities:
                visiting_city = cities_dict[visiting_city_name]
                visiting_city.add_clinic_site(clinic, direction='visiting')
            for leaving_city_name in clinic.leaving_cities:
                leaving_city = cities_dict[leaving_city_name]
                leaving_city.add_clinic_site(clinic, direction='leaving')




