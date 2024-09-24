

class Entity:
    pass


class LineAlgorithmData:

    def __init__(self):
        self.x_data = None
        self.y_data = None


class LineVisualData:

    def __init__(self):
        self.linewidth = None
        self.color = None
        self.edgecolor = None


class Line(Entity):

    def __init__(self):
        self.line_algorithm_data = LineAlgorithmData()
        self.line_visual_data = LineVisualData()


class CityScatterAlgorithmData:

    def __init__(self):
        self.coordinate = None


class CityScatterVisualData:

    def __init__(self):
        self.size = None
        self.color = None
        self.edgecolor = None
        self.marker = None
        self.label = None


class CityScatter(Entity):

    def __init__(self):
        self.city_scatter_algorithm_data = CityScatterAlgorithmData()
        self.city_scatter_visual_data = CityScatterVisualData()


class CityTextBoxAlgorithmData:

    def __init__(self):
        self.text_box_dimensions = None


class CityTextBoxVisualData:

    def __init__(self):
        self.edgecolor = None


class CityTextBox(Entity):

    def __init__(self):
        self.city_text_box_algorithm_data = CityTextBoxAlgorithmData()
        self.city_text_box_visual_data = CityTextBoxVisualData()


class CityEntity:

    def __init__(self, city_scatter: CityScatter, city_text_box: CityTextBox):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box
