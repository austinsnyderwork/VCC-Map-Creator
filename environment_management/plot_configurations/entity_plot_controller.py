from typing import Union

import config_manager
import entities
from entity_conditions_maps import ConditionsMap


class MapDisplayController:

    def __init__(self, **plot_settings):
        self.config = config_manager.ConfigManager()
        self.plot_settings = plot_settings

    def should_display(self, entity: entities.Entity, iteration: int) -> bool:

    def get_config_value(self, key, default_type):
        if self.plot_settings[key]:
            return self.plot_settings[key]

        return self.config.get_config_value(key, default_type)


class AlgorithmDisplayController:

    def __init__(self, **plot_settings):
        self.config = config_manager.ConfigManager()
        self.plot_settings = plot_settings

        self.entity_display_origin_outpatient = {
            entities.CityScatter: {
                'origin': self.get_config_value('algo_display.show_origin_scatters', bool),
                'outpatient': self.get_config_value('algo_display.show_origin_outpatients', bool)
            },
            entities.CityTextBox: {
                'origin': self.get_config_value('algo_display.show_origin_text_box', bool),
                'outpatient': self.get_config_value('algo_display.show_outpatient_text_box', bool)
            }
        }

        self.entities_display = {
            entities.TextBoxScan: self.get_config_value('algo_display.show_scan_poly', bool),
            entities.TextBoxSearchArea: self.get_config_value('algo_display.show_search_area_poly', bool),
            entities.TextBoxFinalist: self.get_config_value('algo_display.show_poly_finalist', bool),
            entities.TextBoxNearbyScanArea: self.get_config_value('algo_display.show_nearby_search_poly', bool)
        }

        self.entity_iterations_display = {
            entities.TextBoxScan: self.get_config_value('algo_display.steps_to_show_scan_poly', int),
            entities.TextBoxSearchArea: self.get_config_value('algo_display.steps_to_show_scan_poly', int),
            entities.TextBoxFinalist: self.get_config_value('algo_display.steps_to_show_poly_finalist', int),
            entities.TextBoxNearbyScanArea: self.get_config_value('algo_display.steps_to_show_poly_finalist', int)
        }

    def should_display(self, entity: entities.Entity, iterations: int) -> bool:
        # Initial general pass
        if type(entity) in self.entity_display_origin_outpatient:
            if not self.entity_display_origin_outpatient[type(entity)][entity.origin_or_outpatient]:
                return False

        if type(entity) in self.entities_display:
            if not self.entities_display[type(entity)][entity.origin_or_outpatient]:
                return False

        if type(entity) in self.entity_iterations_display:
            if iterations != self.entity_iterations_display[type(entity)]:
                return False

        return True

    def get_config_value(self, key, default_type):
        if self.plot_settings[key]:
            return self.plot_settings[key]

        return self.config.get_config_value(key, default_type)

class EntityDisplayController:

    def __init__(self,
                 entity_conditions_map: ConditionsMap = None,
                 config: config_manager.ConfigManager = None,
                 **plot_settings):
        self.map_display_controller = MapDisplayController()
        self.algorithm_display_controller = AlgorithmDisplayController()
        self.config = config if config else config_manager.ConfigManager()
        self.entity_conditions_map = entity_conditions_map
        self.plot_settings = plot_settings


    def determine_display(self, entity: entities.Entity, iterations: int, display_type: str, **kwargs) -> Union[entities.Entity, None]:
        display_funcs = {
            'map': self.map_display_controller.should_display,
            'algorithm': self.algorithm_display_controller.should_display
        }
        if not display_funcs[display_type](entity, iterations):
            return None

        if not 



