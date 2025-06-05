
import mapping
from . import PlotController
from .visualization_element_result import VisualizationElementResult


class PlotManager:

    def __init__(self,
                 algorithm_handler,
                 map_plotter: mapping.MapPlotter,
                 plot_controller: PlotController):
        self.algorithm_handler = algorithm_handler
        self.map_plotter = map_plotter
        self.plot_controller = plot_controller

    def attempt_plot_algorithm_element(self, vis_element_result: VisualizationElementResult):
        if self.plot_controller.should_display(
                vis_element=vis_element_result.vis_element,
                display_type='text_box_algorithm',
                iterations=vis_element_result.num_iterations):
            self.algorithm_handler.plot_element(vis_element_result.vis_element)
            return True
        return False
