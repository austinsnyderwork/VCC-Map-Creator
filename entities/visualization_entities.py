

class Entity:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.city_scatter_algorithm_data = CityScatterAlgorithmData()
        self.city_scatter_visual_data = CityScatterVisualData()

        algo_variables = set()

        visual_variables = ('color', 'size')


class CityTextBoxAlgorithmData:

    def __init__(self):
        self.text_box_dimensions = None


class CityTextBoxVisualData:

    def __init__(self):
        self.edgecolor = None


class CityTextBox(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.city_text_box_algorithm_data = CityTextBoxAlgorithmData()
        self.city_text_box_visual_data = CityTextBoxVisualData()


class TextBoxScan(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TextBoxSearchArea(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TextBoxNearbyScanArea(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TextBoxFinalist(Entity):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

