import copy

from entities.entity_classes import ProviderAssignment, City
from entities.factory import EntitiesContainer
from plot_maps.base_classes import ConditionsController


class HighestOriginVolumeController(ConditionsController):

    def __init__(self, entities_container: EntitiesContainer):
        self._entities_container = self._filter_entities_container(entities_container=entities_container,
                                                                   origin_cities_limit=origin_cities_limit)
        
        self._city_volumes = dict()
        
        self._setup()

        self.entity_types = [City, ProviderAssignment]

        super().__init__(conditions_map, **kwargs)

    def _setup(self):
        origin_cities_limit = 5
        
        for city in self._entities_container.cities:
            num_worksites = len(city.worksites)
            if num_worksites not in self._city_volumes:
                self._city_volumes[num_worksites] = set()

            self._city_volumes[num_worksites].add(city)

        highest_volumes = sorted(list(self._city_volumes.keys()), reverse=True)[:5]
        origin_cities = set()
        for volume in highest_volumes:
            origin_cities.update(self._city_volumes[volume])
            if len(origin_cities) >= origin_cities_limit:
                break

        # Filter EntitiesContainer based on the high volume origin cities
        entities_container = copy.deepcopy(self._entities_container)
        valid_provider_assignments = set(
            pa for pa in entities_container.provider_assignments
            if pa.origin_city in origin_cities
        )
        entities_container.provider_assignments = valid_provider_assignments
        valid_cities = set()
        valid_worksites = set()
        for pa in valid_provider_assignments:
            valid_cities.add(pa.origin_city)
            valid_cities.add(pa.visiting_city)

            valid_worksites.add(pa.origin_site)
            valid_worksites.add(pa.visiting_site)
        entities_container.cities = valid_cities
        entities_container.worksites = valid_worksites

        return entities_container
    