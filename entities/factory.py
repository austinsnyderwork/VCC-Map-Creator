import pandas as pd

from shared.shared_utils import Coordinate
from .entity_classes import City, Worksite, Provider, ProviderAssignment, AssignmentDirection


class EntitiesContainer:
    
    def __init__(self):
        
        self.cities = set()
        self.worksites = set()
        self.providers = set()
        self.provider_assignments = set()

    @property
    def entities(self):
        return self.cities | self.worksites | self.providers | self.provider_assignments

class EntitiesFactory:

    @staticmethod
    def _handle_new_entity(entity, dict_: dict):
        if entity not in dict_:
            entity.cities[entity] = entity
    
        origin_city = dict_[entity]
    
        return origin_city
    
    @classmethod
    def _apply_create_entities(cls, row, container: EntitiesContainer):
        origin_city = City(
            city_name=row['origin_city'],
            city_coord=Coordinate(
                longitude=row['origin_lon'],
                latitude=row['origin_lat']
            )
        )
        origin_city = cls._handle_new_entity(entity=origin_city, dict_=container.cities)
    
        visiting_city = City(
            city_name=row['visiting_city'],
            city_coord=Coordinate(
                longitude=row['visiting_lon'],
                latitude=row['visiting_lat']
            )
        )
        visiting_city = cls._handle_new_entity(entity=visiting_city, dict_=container.cities)
    
        origin_worksite = Worksite(
            site_name=row['origin_site'],
            city=origin_city
        )
        origin_worksite = cls._handle_new_entity(entity=origin_worksite, dict_=container.worksites)
    
        visiting_worksite = Worksite(
            site_name=row['visiting_site'],
            city=visiting_city
        )
        visiting_worksite = cls._handle_new_entity(entity=visiting_worksite, dict_=container.worksites)
    
        provider = Provider(
            name=row['consultant_name'],
            hcp_id=row['hcp_id']
        )
        provider = cls._handle_new_entity(entity=provider, dict_=container.providers)
    
        provider_assignment = ProviderAssignment(
            provider=provider,
            specialty=row['specialty'],
            origin_site=origin_worksite,
            visiting_site=visiting_worksite
        )
        container.provider_assignments.add(provider_assignment)
        origin_worksite.add_assignment(
            direction=AssignmentDirection.LEAVING,
            provider_assignment=provider_assignment
        )
        visiting_worksite.add_assignment(
            direction=AssignmentDirection.VISITING,
            provider_assignment=provider_assignment
        )
    
    @classmethod
    def create_entities(cls, df: pd.DataFrame) -> EntitiesContainer:
        container = EntitiesContainer()
        df.apply(cls._apply_create_entities, args=(container,))
        return container

