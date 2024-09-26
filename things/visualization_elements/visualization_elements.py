from abc import ABC

class VisualizationElement(ABC):
    pass


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
        super().__init__()
        self.line_algorithm_data = LineAlgorithmData(**kwargs)
        self.line_visual_data = LineVisualData(**kwargs)

    def __getattr__(self, item):
        if hasattr(self.line_algorithm_data, item):
            return getattr(self.line_algorithm_data, item)
        elif hasattr(self.line_visual_data, item):
            return getattr(self.line_visual_data, item)


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
        super().__init__()
        self.city_scatter_algorithm_data = CityScatterAlgorithmData()
        self.city_scatter_visual_data = CityScatterVisualData()

    def __getattr__(self, item):
        if hasattr(self.city_scatter_algorithm_data, item):
            return getattr(self.city_scatter_algorithm_data, item)
        elif hasattr(self.city_scatter_visual_data, item):
            return getattr(self.city_scatter_visual_data, item)


class CityTextBoxAlgorithmData:

    def __init__(self, **kwargs):
        self.text_box_dimensions = kwargs['text_box_dimensions']

    @property
    def centroid(self):
        text_box_width = self.text_box_dimensions['x_max'] - self.text_box_dimensions['x_min']
        text_box_height = self.text_box_dimensions['y_max'] - self.text_box_dimensions['y_min']

        lon = self.text_box_dimensions['x_min'] + (text_box_width / 2)
        lat = self.text_box_dimensions['y_min'] + (text_box_height / 2)

        return lon, lat


class CityTextBoxVisualData:

    def __init__(self, **kwargs):
        self.city_name = kwargs['city_name']
        self.fontsize = kwargs['font_size']
        self.font = kwargs['font']
        self.color = kwargs['color']
        self.fontweight = kwargs['fontweight']


class CityTextBox(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__()
        self.city_text_box_algorithm_data = CityTextBoxAlgorithmData(**kwargs)
        self.city_text_box_visual_data = CityTextBoxVisualData(**kwargs)

    def __getattr__(self, item):
        if hasattr(self.city_text_box_algorithm_data, item):
            return getattr(self.city_text_box_algorithm_data, item)
        elif hasattr(self.city_text_box_visual_data, item):
            return getattr(self.city_text_box_visual_data, item)


class CityScatterAndText:

    def __init__(self, city_scatter: CityScatter, city_text_box: CityTextBox):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box


class TextBoxScan(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__()


class TextBoxScanArea(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__()


class TextBoxNearbySearchArea(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__()


class TextBoxFinalist(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__()


class Intersection(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__()

