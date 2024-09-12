

class VisualizationElement:

    def __init__(self, element_type: str, **kwargs):
        self.element_type = element_type

        for k, v in kwargs.items():
            setattr(self, k, v)

    def add_value(self, element: str, value):
        setattr(self, element, value)

