import logging
import map_creation
from algorithm import rtree_analysis

import algorithm
import input_output

class Interface:

    def __init__(self):
        self.vis_map_creator = map_creation.VisualizationMapCreator()
        self.algorithm_handler = algorithm.AlgorithmHandler()
        self.rtree_analyzer = rtree_analysis.RtreeAnalyzer()

        self.city_coords = {}

    def _add_city_gpd_coord(self, row):
        community = row['community']
        origin = row['point_of_origin']
        if community not in self.city_coords:
            self.city_coords[community] = {
                'latitude': row['to_lat'],
                'longitude': row['to_lon']
            }

        if origin not in self.city_coords:
            self.city_coords[origin] = {
                'latitude': row['origin_lat']
                'longitude': row['origin_lon']
            }

    def import_data(self, vcc_file_name: str, sheet_name:str = None, variables: dict = None):
        df = input_output.get_dataframe(file_name=vcc_file_name,
                                        sheet_name=sheet_name,
                                        variables=variables)

        # Gather necessary city coordinates
        df.apply(self._add_city_gpd_coord, axis=1)
        logging.info("Added city coords.")
