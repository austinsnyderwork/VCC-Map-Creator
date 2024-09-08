import map_creation
import spatial_analysis


class Interface:

    def __init__(self):
        self.map_creator = map_creation.MapCreator()
        self.rtree_analyzer = spatial_analysis.RtreeAnalyzer()

    def run_map_creation(self):
