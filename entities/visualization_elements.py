

class Line:

    def __init__(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data


class CityScatter:

    def __init__(self, city_name: str, site_type: str):
        self.city_name = city_name
        self.site_type = site_type


class CityTextBox:

    def __init__(self, city_name: str):
        self.city_name = city_name


class CityEntities:

    def __init__(self, city_scatter: CityScatter, city_text_box: CityTextBox):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box