

from entity_conditions_maps import ConditionsMap


class EntityPlotController:

    def __init__(self,
                 entity_conditions_map: ConditionsMap = None,
                 should_plot_origin_lines: bool = True,
                 should_plot_outpatient_lines: bool = True,
                 should_plot_origin_scatters: bool = True,
                 should_plot_outpatient_scatters: bool = True,
                 should_plot_origin_text_box: bool = True,
                 should_plot_outpatient_text_box: bool = True):
        self.entity_conditions_map = entity_conditions_map
        self.should_plot_origin_lines = should_plot_origin_lines
        self.should_plot_outpatient_lines = should_plot_outpatient_lines
        self.should_plot_origin_scatters = should_plot_origin_scatters
        self.should_plot_outpatient_scatters = should_plot_outpatient_scatters
        self.should_plot_origin_text_box = should_plot_origin_text_box
        self.should_plot_outpatient_text_box = should_plot_outpatient_text_box



