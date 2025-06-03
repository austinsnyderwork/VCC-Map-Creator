
from visualization_elements import vis_element_classes


class VisualizationElementResult:

    def __init__(self, vis_element: vis_element_classes.VisualizationElement, num_iterations: int = None,
                 city_text_box_iterations: int = None, new_max_score: bool = False, force_show: bool = False):
        self.vis_element = vis_element
        self.num_iterations = num_iterations
        self.city_text_box_iterations = city_text_box_iterations
        self.new_max_score = new_max_score
        self.force_show = force_show

