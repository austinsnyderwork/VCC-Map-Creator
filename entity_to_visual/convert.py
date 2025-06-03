
from config_manager import ConfigManager

class EntityToVisualizationElement:

    def __init__(self, config: ConfigManager = None):
        self.config = config or ConfigManager()

    def convert_city_to_scatter(self):
        
