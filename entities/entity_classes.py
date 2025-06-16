from abc import ABC, abstractmethod
from enum import Enum

from shared.shared_utils import Coordinate


class AssignmentDirection(Enum):
    VISITING = 'visiting'
    LEAVING = 'leaving'


class Entity(ABC):

    @property
    @abstractmethod
    def _key(self):
        pass

    def __hash__(self):
        return hash(self._key)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return self._key == other._key


class Provider(Entity):

    def __init__(self, name: str):
        self.provider_name = name

    @property
    def _key(self):
        return self.provider_name


class City(Entity):

    def __init__(self, city_name: str, city_coord: Coordinate):
        self.city_name = city_name
        self.city_coord = city_coord

    @property
    def _key(self):
        return self.city_name


class ProviderAssignment(Entity):

    def __init__(self, provider: Provider, specialty: str, origin_site: 'Worksite', visiting_site: 'Worksite'):
        self.provider = provider
        self.specialty = specialty
        self.origin_site = origin_site
        self.visiting_site = visiting_site

    @property
    def _key(self):
        return self.provider, self.specialty, self.origin_site, self.visiting_site

    @property
    def origin_city(self):
        return self.origin_site.city

    @property
    def visiting_city(self):
        return self.visiting_site.city


class Worksite(Entity):

    def __init__(self, site_name: str, city: 'City'):
        self.site_name = site_name
        self.city = city
        
        self._provider_assignments = {
            AssignmentDirection.LEAVING: set(),
            AssignmentDirection.VISITING: set()
        }

    @property
    def _key(self):
        return self.site_name, self.city

    def add_assignment(self, provider_assignment: ProviderAssignment, direction: AssignmentDirection):
        self._provider_assignments[direction].add(provider_assignment)

    @property
    def visiting_specialties(self) -> set[str]:
        specialties = set(provider_assignment.specialty 
                          for provider_assignment in self._provider_assignments[AssignmentDirection.VISITING])
        return specialties


