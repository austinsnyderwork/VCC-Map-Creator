import pandas as pd

from shared.shared_utils import Coordinate
from .entity_classes import City, Worksite, Provider, ProviderAssignment, AssignmentDirection


class EntitiesContainer:
    
    def __init__(self):

        self.entities_map = {
            City: dict(),
            Worksite: dict(),
            Provider: dict(),
            ProviderAssignment: dict()
        }

    @property
    def cities(self) -> set[City]:
        return set(self.entities_map[City].values())

    @property
    def worksites(self) -> set[Worksite]:
        return set(self.entities_map[Worksite].values())

    @property
    def providers(self) -> set[Provider]:
        return set(self.entities_map[Provider].values())

    @property
    def provider_assignments(self) -> set[ProviderAssignment]:
        return set(self.entities_map[ProviderAssignment].values())

    @property
    def entities(self):
        r = set()
        for e_class, d in self.entities_map.items():
            r.update(set(d.values()))

        return r

    def add_entity(self, entity):
        d = self.entities_map[type(entity)]
        if entity not in d:
            d[entity] = entity

        return d[entity]


class EntitiesFactory:
    
    @classmethod
    def _apply_create_entities(cls, row, container: EntitiesContainer):
        origin_city = City(
            city_name=row['origin_city'],
            city_coord=Coordinate(
                longitude=row['origin_lon'],
                latitude=row['origin_lat']
            )
        )
        origin_city = container.add_entity(entity=origin_city)
    
        visiting_city = City(
            city_name=row['visiting_city'],
            city_coord=Coordinate(
                longitude=row['visiting_lon'],
                latitude=row['visiting_lat']
            )
        )
        visiting_city = container.add_entity(visiting_city)
    
        origin_worksite = Worksite(
            site_name=row['origin_site'],
            city=origin_city
        )
        origin_worksite = container.add_entity(origin_worksite)
    
        visiting_worksite = Worksite(
            site_name=row['visiting_site'],
            city=visiting_city
        )
        visiting_worksite = container.add_entity(visiting_worksite)
    
        provider = Provider(
            name=row['consultant_name']
        )
        provider = container.add_entity(provider)
    
        provider_assignment = ProviderAssignment(
            provider=provider,
            specialty=row['specialty'],
            origin_site=origin_worksite,
            visiting_site=visiting_worksite
        )
        pa = container.add_entity(provider_assignment)

        origin_worksite.add_assignment(
            direction=AssignmentDirection.LEAVING,
            provider_assignment=pa
        )
        visiting_worksite.add_assignment(
            direction=AssignmentDirection.VISITING,
            provider_assignment=pa
        )
    
    @classmethod
    def create_entities(cls, df: pd.DataFrame) -> EntitiesContainer:
        container = EntitiesContainer()
        df.apply(cls._apply_create_entities, args=(container,), axis=1)

        return container

