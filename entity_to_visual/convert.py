
from config_manager import ConfigManager
from entities.entity_classes import City


class EntityToVisualElement:

    def __init__(self, config: ConfigManager = None):
        self.config = config or ConfigManager()

    def convert_city_to_scatter(self, city: City):


