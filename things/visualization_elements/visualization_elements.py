

def get_kwarg(kwarg, key, default):
    return kwarg[key] if key in kwarg else default


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
        self.algorithm_data = get_kwarg(kwargs, 'algorithm', algorithm_data_class())
        self.map_data = get_kwarg(kwargs, 'map', map_data_class())

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
        self.x_data = get_kwarg(kwargs, 'x_data', None)
        self.y_data = get_kwarg(kwargs, 'y_data', None)

        self.color = get_kwarg(kwargs, 'color', None)


class LineMapData:

    def __init__(self, **kwargs):
        self.linewidth = get_kwarg(kwargs, 'linewidth', None)
        self.color = get_kwarg(kwargs, 'color', None)
        self.edgecolor = get_kwarg(kwargs, 'edgecolor', None)


class Line(DualVisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(algorithm_data_class=LineAlgorithmData,
                         map_data_class=LineMapData,
                         **kwargs)


class CityScatterAlgorithmData:

    def __init__(self, **kwargs):
        self.coordinate = get_kwarg(kwargs, 'coordinate', None)


class CityScatterMapData:

    def __init__(self, **kwargs):
        self.size = get_kwarg(kwargs, 'size', None)
        self.color = get_kwarg(kwargs, 'color', None)
        self.edgecolor = get_kwarg(kwargs, 'color', None)
        self.marker = get_kwarg(kwargs, 'marker', None)
        self.label = get_kwarg(kwargs, 'label', None)


class CityScatter(DualVisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(algorithm_data_class=CityScatterAlgorithmData,
                         map_data_class=CityScatterMapData,
                         **kwargs)


class CityTextBoxAlgorithmData:

    def __init__(self, **kwargs):
        self.text_box_dimensions = get_kwarg(kwargs, 'text_box_dimension', None)

    @property
    def centroid(self):
        text_box_width = self.text_box_dimensions['x_max'] - self.text_box_dimensions['x_min']
        text_box_height = self.text_box_dimensions['y_max'] - self.text_box_dimensions['y_min']

        lon = self.text_box_dimensions['x_min'] + (text_box_width / 2)
        lat = self.text_box_dimensions['y_min'] + (text_box_height / 2)

        return lon, lat


class CityTextBoxMapData:

    def __init__(self, **kwargs):
        self.city_name = get_kwarg(kwargs, 'city_name', None)
        self.fontsize = get_kwarg(kwargs, 'font_size', None)
        self.font = get_kwarg(kwargs, 'font', None)
        self.color = get_kwarg(kwargs, 'color', None)
        self.fontweight = get_kwarg(kwargs, 'fontweight', None)


class CityTextBox(DualVisualizationElement):

    def __init__(self, **kwargs):
        super().__init__(algorithm_data_class=CityTextBoxAlgorithmData,
                         map_data_class=CityTextBoxMapData,
                         **kwargs)


class CityScatterAndText:

    def __init__(self, city_scatter: CityScatter, city_text_box: CityTextBox):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box

    def __getattr__(self, item):
        if item in super().__getattribute__('__dict__'):
            return super().__getattribute__(item)
        elif hasattr(self.city_scatter, item):
            return getattr(self.city_scatter, item)
        elif hasattr(self.city_text_box, item):
            return getattr(self.city_text_box, item)
        else:
            raise AttributeError(f"Could not find attribute {item} in CityScatterAndText object.")


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

