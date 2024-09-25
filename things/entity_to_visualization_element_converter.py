from things.entities import entities
import config_manager
import environment_management
from visualization_elements import visualization_elements


class EntityToVisualizationElementConverter:

    def __init__(self, config: config_manager.ConfigManager, city_origin_network_handler: environment_management.CityOriginNetworkHandler):
        self.config = config
        self.city_origin_network_handler = city_origin_network_handler

        self.entity_to_vis_element_map = {
            entities.City: [visualization_elements.CityScatter, visualization_elements.CityTextBox],
            entities.ProviderAssignment: visualization_elements.Line
        }

        self.scatter_marker_map = {
            'dual_origin_visiting': self.config.get_config_value('viz_display.dual_origin_outpatient_marker', str),
            'origin': self.config.get_config_value('viz_display.origin_marker', str),
            'visiting': self.config.get_config_value('viz_display.visiting_marker', str)
        }

    def _get_city_visualization_element_data(self, city_entity: entities.City):
        scatter_data = {
            'color': self.city_origin_network_handler.get_entity_color(entity=city_entity),
            'edgecolor': self.city_origin_network_handler.get_entity_color(entity=city_entity),
            'marker': self.scatter_marker_map[city_entity.site_type],
            'size': self.config.get_config_value(key='viz_display.scatter_size', cast_type=int),
            'label': city_entity.site_type
        }
        return scatter_data

    def _get_provider_assignment_visualization_element_data(self, assignment_entity: entities.ProviderAssignment):
        line_data = {

        }

    def convert_entity(self, entity: entities.Entity):
        if type(entity) is entities.ProviderAssignment:
            line_data = {

            }
        elif type(entity) is entities.City:
            scatter_data = self._get_city_visualization_element_data(entity)
            return visualization_elements.CityScatter(**scatter_data)
