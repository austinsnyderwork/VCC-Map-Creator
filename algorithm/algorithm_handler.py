import logging

from . import rtree_analyzer
import config_manager
from algorithm.city_scanning.city_scanner import CityScanner
from .algo_utils import helper_functions
from . import spatial_analysis
from .algorithm_plotter import AlgorithmPlotter
from things.visualization_elements import visualization_elements


class AlgorithmHandler:

    def __init__(self, config: config_manager.ConfigManager):
        self.config = config
        self.algo_map_plotter = AlgorithmPlotter(
            display_fig_size=(self.config.get_config_value('display.fig_size_x', int), self.config.get_config_value('display.fig_size_y', int)),
            county_line_width=self.config.get_config_value('display.county_line_width', float),
            show_display=self.config.get_config_value('algo_display.show_display', bool))
        self.rtree_analyzer = rtree_analyzer.RtreeAnalyzer()

    def plot_element(self, element: visualization_elements.VisualizationElement):
        element_poly_classes = {
            visualization_elements.Line: 'line',
            visualization_elements.CityScatter: 'scatter',
            visualization_elements.CityTextBox: 'text'
        }
        self.algo_map_plotter.plot_element(element)
        self.rtree_analyzer.add_poly(poly_class=element_poly_classes[type(element)],
                                     poly=element.algorithm_poly)

    def _handle_city_text_box_search(self, city_text_box_search: CityScanner) -> visualization_elements.TextBoxScan:

        for result in city_text_box_search.find_best_poly(rtree_analyzer_=self.rtree_analyzer):
            poly_data = lookup_poly_characteristics(poly_type=result.poly_type)
            show_algo_for_poly = should_show_algo(poly_data=poly_data,
                                                  poly_type=result.poly_type,
                                                  num_iterations=result.num_iterations,
                                                  city_name=city_text_box_search.city_name,
                                                  new_max_score=result.new_max_score,
                                                  force_show=result.force_show)
            if show_algo_for_poly:
                if result.poly_type in remove_polys_by_type:
                    polys_to_remove = remove_polys_by_type[result.poly_type]
                    for remove_poly_type in polys_to_remove:
                        if remove_poly_type == 'intersecting':
                            if len(poly_patches['intersecting']) > 0:
                                for idx in reversed(range(len(poly_patches['intersecting']))):
                                    i_patch = poly_patches['intersecting'][idx - 1]
                                    self.algo_map_creator.remove_patch_from_map(i_patch)
                                    poly_patches['intersecting'].pop(idx - 1)
                        elif poly_patches[remove_poly_type]:
                            self.algo_map_creator.remove_patch_from_map(poly_patches[remove_poly_type])
                            poly_patches[remove_poly_type] = None

                temp_show_pause = show_pause
                if result.new_max_score:
                    temp_show_pause = show_pause + extra_pause_for_new_max_score
                if result.force_show:
                    temp_show_pause = temp_show_pause + extra_pause_for_force_show
                patch = self.algo_map_creator.add_poly_to_map(poly=result.poly,
                                                              show_pause=temp_show_pause,
                                                              **poly_data)
                # Load patch into appropriate scan history
                if patch:
                    if result.poly_type == 'scan':
                        poly_patches['scan'] = patch
                    if result.poly_type == 'nearby_search':
                        poly_patches['nearby_search'] = patch
                    elif result.poly_type == 'intersecting':
                        poly_patches['intersecting'].append(patch)
                    elif result.poly_type == 'finalist':
                        poly_patches['finalist'] = patch
                    elif result.poly_type == 'best':
                        poly_patches['best'] = patch

            if result.poly_type == 'best':
                return result.poly

    def find_best_polygon(self, city_element: visualization_elements.CityScatter,
                          text_box_element: visualization_elements.CityTextBox):
        logging.info(f"Finding best poly for {city_element.city_name}")
        city_text_box_search = CityScanner(
            config=self.config,
            text_box=text_box_element.algorithm_box_geometry,
                                           city_poly=city_element.algorithm_poly)
        best_poly = self._handle_city_text_box_search(city_text_box_search=city_text_box_search)
        logging.info(f"Found best poly for {city_element.city_name}.")
        city_element.best_poly = best_poly

        poly_data = lookup_poly_characteristics(poly_type='best')
        show_poly = should_show_algo(poly_data=poly_data,
                                     poly_type='best',
                                     city_name=city_element.city_name)
        if show_poly:
            self.algo_map_plotter.plot_element(poly=best_poly,
                                                  **poly_data)
        self.rtree_analyzer.add_poly(poly=best_poly,
                                     poly_class='text')
