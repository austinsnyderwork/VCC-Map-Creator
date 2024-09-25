import logging

import entities
from .worksite_grouping import CityOriginNetworkHandler


class Environment:

    def __init__(self, cities_directory: entities.CitiesDirectory,
                 city_origin_network_handler: CityOriginNetworkHandler):
        self.entities_manager = entities.EntitiesManager()

    def add_city(self, city: entities.City):
        self.entities_manager.add_entity(city)

    def add_clinic(self, clinic: entities.VccClinicSite, direction: str):
        if clinic.name in self.clinic_sites:
            return

        clinic_city = self.cities_directory.get_city(name=clinic.city_name)
        clinic_city.add_clinic(clinic=clinic,
                               direction=direction)

        self.clinic_sites[clinic.name] = clinic

    def add_provider(self, provider: entities.Provider, origin_site_name: str, outpatient_site_name: str):
        origin_site = self.clinic_sites[origin_site_name]
        outpatient_site = self.clinic_sites[outpatient_site_name]

        origin_site.add_provider(provider=provider,
                                 direction='leaving')
        outpatient_site.add_provider(provider=provider,
                                     direction='visiting')





