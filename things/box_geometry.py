

class BoxGeometry:

    def __init__(self, dimensions: dict):
        self.dimensions = dimensions

    @classmethod
    def BoxGeometryFromCoordinate(cls, centroid: tuple, width: int, height: int):
        lon, lat = centroid
        dimensions = {
            'x_min': lon - width,
            'y_min': lat - height,
            'x_max': lon + width,
            'y_max': lat + height
        }
        return cls(dimensions=dimensions)

    def add_buffer(self, buffer_amount: float):
        dimensions = self.dimensions.copy()
        for dimension, value in dimensions.items():
            if dimension in ['x_max', 'y_max']:
                dimensions[dimension] = value + buffer_amount
            elif dimension in ['x_min', 'y_min']:
                dimensions[dimension] = value - buffer_amount
            else:
                raise ValueError(f"Dimension {dimension} not one of acceptable dimensions: "
                                 f"['x_max', 'y_max', 'x_min', 'y_min'.")
        return dimensions

    @property
    def width(self):
        return self.dimensions['x_max'] - self.dimensions['x_min']

    @property
    def height(self):
        return self.dimensions['y_max'] - self.dimensions['y_min']

    @property
    def centroid(self):
        x = self.dimensions['x_min'] + (self.width / 2)
        y = self.dimensions['y_min'] + (self.height / 2)
        return x, y

    @property
    def x_min(self):
        return self.dimensions['x_min']

    @property
    def x_max(self):
        return self.dimensions['x_max']

    @property
    def y_min(self):
        return self.dimensions['y_min']

    @property
    def y_max(self):
        return self.dimensions['y_max']
    
    def reduce_width(self, percent_width_change: float):
        if percent_width_change < 1.0:
            percent_width_change = (percent_width_change / 100)
        width_change_total = self.width * percent_width_change
        self.dimensions['x_max'] += width_change_total / 2
        self.dimensions['x_min'] -= width_change_total / 2

    def reduce_height(self, percent_height_change: float):
        if percent_height_change < 1.0:
            percent_height_change = (percent_height_change / 100)
        height_change_total = self.height * percent_height_change
        self.dimensions['x_max'] += height_change_total / 2
        self.dimensions['x_min'] -= height_change_total / 2

    def move_box(self, direction: str, amount: float):
        if direction == 'up':
            self.dimensions['y_min'] += amount
            self.dimensions['y_max'] += amount
        elif direction == 'down':
            self.dimensions['y_min'] -= amount
            self.dimensions['y_max'] -= amount
        elif direction == 'right':
            self.dimensions['x_min'] += amount
            self.dimensions['x_max'] += amount
        elif direction == 'left':
            self.dimensions['x_min'] -= amount
            self.dimensions['x_max'] -= amount


