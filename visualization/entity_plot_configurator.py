

class Scatter:

    def __init__(self, size: int, color: str, marker: str, edgecolor: str, label: str):
        self.size = size
        self.color = color
        self.edgecolor = edgecolor
        self.marker = marker
        self.label = label


class EntityCondition:

    def __init__(self, condition, scatter: Scatter, **kwargs):
        self.condition = condition
        self.scatter = scatter


class ScatterPlotConfigurator:

    def __init__(self, conditions: list[EntityCondition] = None):
        self.conditions = conditions if conditions else []

    def add_condition(self, condition, color: str, size: int, marker: str, edgecolor: str, label: str):
        entity = Scatter(size=size,
                          color=color,
                          marker=marker,
                          edgecolor=edgecolor,
                          label=label)

        new_condition = EntityCondition(condition=condition, entity=entity)
        self.conditions.append(new_condition)

    def get_scatter(self, **kwargs):
        for condition in self.conditions:
            if condition.condition(**kwargs):
                return condition.scatter



