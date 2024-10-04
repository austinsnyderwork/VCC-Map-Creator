
from things.visualization_elements import visualization_elements


class VisualizationElementResult:

    def __init__(self, vis_element: visualization_elements.VisualizationElement, num_iterations: int = None,
                 new_max_score: bool = False, force_show: bool = False):
        self.vis_element = vis_element
        self.num_iterations = num_iterations
        self.new_max_score = new_max_score
        self.force_show = force_show

