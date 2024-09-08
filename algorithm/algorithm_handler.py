import configparser
from shapely import Polygon

from . import algorithm_map_creator, poly_creation, rtree_analysis


config = configparser.ConfigParser()
config.read('config.ini')

class AlgorithmHandler:

    def __init__(self, should_show_map):
        self.algo_map_creator = algorithm_map_creator.AlgorithmMapCreator()
        self.rtree_analyzer = rtree_analysis.RtreeAnalyzer()

    def add_polys(self, polys_data: dict):
        acceptable_poly_types = ['line', 'rectangle', 'scatter']

        new_polys = []
        for poly_type, poly_data in polys_data:
            if poly_type not in acceptable_poly_types:
                raise ValueError(f"Poly types passed into add_polys are not one of acceptable poly types:\n\tAcceptable: "
                                 f"{acceptable_poly_types}\n\tPassed in: {poly_type}")
            poly = poly_creation.create_poly(poly_type=poly_type,
                                             kwargs=poly_data)
            new_polys.append(poly)
        for poly in new_polys:
            self.rtree_analyzer.add_poly(poly=poly)
            if config['algorithm']['show_map']:
                self.algo_map_creator.add_poly()

