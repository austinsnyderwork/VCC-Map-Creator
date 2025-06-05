
from enum import Enum

from shared.shared_utils import Coordinate


class AssignmentDirection(Enum):
    VISITING = 'visiting'
    LEAVING = 'leaving'


class Provider:

    def __init__(self, name: str, hcp_id: int):
        self.provider_name = name
        self.hcp_id = hcp_id

    def __hash__(self):
        return self.hcp_id

    def __eq__(self, other):
        if not isinstance(other, Provider):
            return False

        return self.provider_name == other.provider_name and self.hcp_id == other.hcp_id


class City:

    def __init__(self, city_name: str, city_coord: Coordinate):
        self.city_name = city_name
        self.city_coord = city_coord

    def __hash__(self):
        return hash((self.city_name, self.city_coord))

    def __eq__(self, other):
        if not isinstance(other, City):
            return False

        return self.city_name == other.city_name and self.city_coord == other.city_coord


class ProviderAssignment:

    def __init__(self, provider: Provider, specialty: str, origin_site: 'Worksite', visiting_site: 'Worksite'):
        self.provider = provider
        self.specialty = specialty
        self.origin_site = origin_site
        self.visiting_site = visiting_site

    def __hash__(self):
        return hash((
            self.provider,
            self.specialty,
            self.origin_site,
            self.visiting_site
        ))

    def __eq__(self, other):
        if not isinstance(other, ProviderAssignment):
            return False

        return (self.provider == other.provider
                and self.specialty == other.specialty
                and self.origin_site == other.origin_site
                and self.visiting_site == other.visiting_site)

    @property
    def origin_city(self):
        return self.origin_site.city

    @property
    def visiting_city(self):
        return self.visiting_site.city


class Worksite:

    def __init__(self, site_name: str, city: 'City'):
        self.site_name = site_name
        self.city = city
        
        self._provider_assignments = {
            AssignmentDirection.LEAVING: set(),
            AssignmentDirection.VISITING: set()
        }

    def __hash__(self):
        return hash((self.site_name, self.city))

    def __eq__(self, other):
        if not isinstance(other, Worksite):
            return False

        return self.site_name == other.site_name and self.city == other.city

    def add_assignment(self, provider_assignment: ProviderAssignment, direction: AssignmentDirection):
        self._provider_assignments[direction].add(provider_assignment)

    @property
    def visiting_specialties(self) -> set[str]:
        specialties = set(provider_assignment.specialty 
                          for provider_assignment in self._provider_assignments[AssignmentDirection.VISITING])
        return specialties


