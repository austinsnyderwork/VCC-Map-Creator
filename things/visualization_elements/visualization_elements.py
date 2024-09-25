

class VisualizationElement:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


class LineAlgorithmData:

    def __init__(self, **kwargs):
        self.x_data = kwargs['x_data']
        self.y_data = kwargs['y_data']


class LineVisualData:

    def __init__(self, **kwargs):
        self.linewidth = kwargs['linewidth']
        self.color = kwargs['color']
        self.edgecolor = kwargs['edgecolor']


class Line(VisualizationElement):

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


class CityScatter(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.city_scatter_algorithm_data = CityScatterAlgorithmData()
        self.city_scatter_visual_data = CityScatterVisualData()


class CityTextBoxAlgorithmData:

    def __init__(self):
        self.text_box_dimensions = None


class CityTextBoxVisualData:

    def __init__(self):
        self.edgecolor = None


class CityTextBox(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.city_text_box_algorithm_data = CityTextBoxAlgorithmData()
        self.city_text_box_visual_data = CityTextBoxVisualData()


class CityScatterAndText:

    def __init__(self, city_scatter: CityScatter, city_text_box: CityTextBox):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box


class TextBoxScan(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TextBoxScanArea(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TextBoxNearbySearchArea(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TextBoxFinalist(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Intersection(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

