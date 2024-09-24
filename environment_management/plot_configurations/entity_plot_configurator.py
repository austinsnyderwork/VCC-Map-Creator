

from entity_conditions_maps import ConditionsMap


class PlotConfigurator:

    def __init__(self,
                 entity_conditions_maps: ConditionsMap,
                 should_plot_origin_lines: bool = True,
                 should_plot_outpatient_lines: bool = True,
                 should_plot_origin_scatters: bool = True,
                 should_plot_outpatient_scatters: bool = True,
                 should_plot_origin_text_box: bool = True,
                 should_plot_outpatient_text_box: bool = True):
        self.should_plot_origin_lines = should_plot_origin_lines
        self.should_plot_outpatient_lines = should_plot_outpatient_lines
        self.should_plot_origin_scatters = should_plot_origin_scatters
        self.should_plot_outpatient_scatters = should_plot_outpatient_scatters
        self.should_plot_origin_text_box = should_plot_origin_text_box
        self.should_plot_outpatient_text_box = should_plot_outpatient_text_box

        self.entity_conditions_map = entity_conditions_maps


class ScatterPlotConfigurator(PlotConfigurator):

    def __init__(self, conditions_map: ConditionsMap, should_plot_origin_lines: bool = False,
                 should_plot_outpatient_lines: bool = False):
        super().__init__(
            should_plot_origin_lines=should_plot_origin_lines,
            should_plot_outpatient_lines=should_plot_outpatient_lines
        )
        self.conditions_map = conditions_map

    def get_entity(self, **kwargs):
        entity = self.conditions_map.get_entity_for_condition(**kwargs)
        return entity
