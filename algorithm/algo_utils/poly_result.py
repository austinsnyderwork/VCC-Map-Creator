

class PolyResult:

    def __init__(self, poly, poly_type, num_iterations, new_max_score: bool = False):
        self.poly = poly
        self.poly_type = poly_type
        self.num_iterations = num_iterations
        self.new_max_score = new_max_score