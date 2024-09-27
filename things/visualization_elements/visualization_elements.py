
class VisualizationElement:
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)


def which_class(s):
    # Find the position of the first period
    period_index = s.find('_')

    # If no period is found, return the original string
    if period_index == -1:
        return s, ""

    # Extract the word before the period
    first_word = s[:period_index]

    # Remove the first word and the period
    remaining_string = s[period_index + 1:]

    return first_word, remaining_string


class DualVisualizationElement(VisualizationElement):

    def __init__(self, algorithm_data_class, map_data_class, **kwargs):
        super().__init__()
        algorithm_kwargs = kwargs['algorithm']
        self.algorithm_data = algorithm_data_class(**algorithm_kwargs)

        map_kwargs = kwargs['map']
        self.map_data = map_data_class(**map_kwargs)

    def __getattr__(self, item):
        type_, item = which_class(item)
        if type_ == 'algorithm' and hasattr(self.algorithm_data, item):
            return getattr(self.algorithm_data, item)
        elif type_ == 'map' and hasattr(self.map_data, item):
            return getattr(self.map_data, item)
        else:
            raise ValueError(f"Failed to get value for '{item}' in the {type_} of {self.__class__.__name__}")


class LineAlgorithmData:

    def __init__(self, **kwargs):
        self.x_data = kwargs['x_data']
        self.y_data = kwargs['y_data']

        self.color = kwargs['color']


class LineMapData:

    def __init__(self, **kwargs):
        self.linewidth = kwargs['linewidth']
        self.color = kwargs['color']
        self.edgecolor = kwargs['edgecolor']


class Line(DualVisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(algorithm_data_class=LineAlgorithmData,
                         map_data_class=LineMapData,
                         **kwargs)


class CityScatterAlgorithmData:

    def __init__(self):
        self.coordinate = None


class CityScatterMapData:

    def __init__(self):
        self.size = None
        self.color = None
        self.edgecolor = None
        self.marker = None
        self.label = None


class CityScatter(DualVisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(algorithm_data_class=CityScatterAlgorithmData,
                         map_data_class=CityScatterMapData,
                         **kwargs)


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


class CityTextBoxMapData:

    def __init__(self, **kwargs):
        self.city_name = kwargs['city_name']
        self.fontsize = kwargs['font_size']
        self.font = kwargs['font']
        self.color = kwargs['color']
        self.fontweight = kwargs['fontweight']


class CityTextBox(DualVisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(algorithm_data_class=CityTextBoxAlgorithmData,
                         map_data_class=CityTextBoxMapData,
                         **kwargs)


class CityScatterAndText:

    def __init__(self, city_scatter: CityScatter, city_text_box: CityTextBox):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box


class TextBoxScan(VisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def bounds(self):
        return self.poly.bounds


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

