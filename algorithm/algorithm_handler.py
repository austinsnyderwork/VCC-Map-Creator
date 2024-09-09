import configparser

from . import algorithm_map_creator, helper_functions, poly_creation, rtree_analysis


config = configparser.ConfigParser()
config.read('config.ini')


class AlgorithmHandler:

    def __init__(self):
        self.algo_map_creator = algorithm_map_creator.AlgorithmMapCreator()
        self.rtree_analyzer = rtree_analysis.RtreeAnalyzer()

        self.poly_types = {}

    def plot_lines(self, line_dicts: list[dict]):
        for line_data in line_dicts:
            poly = poly_creation.create_poly(poly_type='line', x_data=line_data['x_data'], y_data=line_data['y_data'],
                                             line_width=line_data['line_width'])
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='line poly')
            self.poly_types[poly] = 'line'
            self.algo_map_creator.add_poly_to_map(poly=poly)

    def plot_scatters(self, point_coords):
        scatter_size = float(config['dimensions']['scatter_size'])
        units_radius_per_1_scatter_size = float(config['dimensions']['units_radius_per_1_scatter_size'])
        for i, point_coord in enumerate(point_coords):
            units_radius = scatter_size * units_radius_per_1_scatter_size
            poly = poly_creation.create_poly(poly_type='scatter', center=point_coord, radius=units_radius)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='scatter poly')
            self.poly_types[poly] = 'point'
            self.algo_map_creator.add_poly_to_map(poly=poly)

    def plot_rectangle(self, lon, lat, color, ):


