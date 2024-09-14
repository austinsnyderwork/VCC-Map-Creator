

class VisualizationElement:

    def __init__(self, element_type: str, **kwargs):
        acceptable_types = ['scatter', 'text_box', 'line']
        if element_type not in acceptable_types:
            raise ValueError(f"Element type {element_type} not in acceptable types {acceptable_types}.")
        self.element_type = element_type

        for k, v in kwargs.items():
            setattr(self, k, v)

    def add_value(self, element: str, value):
        setattr(self, element, value)

