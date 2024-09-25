
from . import entities
from visualization_elements import visualization_elements

class EntityToVisualizationElementConverter:

    def __init__(self):
        entity_to_vis_element_map = {
            entities.City: [visualization_elements.CityScatter, visualization_elements.CityTextBox],
            entities.ProviderAssignment: visualization_elements.Line
        }

    def convert_entity(self, entity: entities.Entity):
        if type(entity) is entities.City:
            scatter_
