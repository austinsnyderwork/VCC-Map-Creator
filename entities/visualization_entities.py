

class Entity:
    pass


class Line(Entity):

    def __init__(self, x_data, y_data):
        self.x_data = x_data
        self.y_data = y_data


class CityScatter(Entity):

    def __init__(self, city_name: str, origin_or_outpatient: str):
        self.city_name = city_name
        self.origin_or_outpatient = origin_or_outpatient


class CityTextBox(Entity):

    def __init__(self, city_name: str):
        self.city_name = city_name


class CityEntities:

    def __init__(self, city_scatter: CityScatter, city_text_box: CityTextBox):
        self.city_scatter = city_scatter
        self.city_text_box = city_text_box
