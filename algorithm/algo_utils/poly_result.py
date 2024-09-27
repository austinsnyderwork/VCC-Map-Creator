

from things.visualization_elements import visualization_elements


class PolyResult:

    def __init__(self, poly: visualization_elements.TextBoxScan, poly_type, num_iterations, new_max_score: bool = False,
                 force_show: bool = False):
        self.poly = poly
        self.poly_type = poly_type
        self.num_iterations = num_iterations
        self.new_max_score = new_max_score
        self.force_show = force_show

