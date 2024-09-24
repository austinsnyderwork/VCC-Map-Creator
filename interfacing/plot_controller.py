import entities


class PlotController:

    def __init__(self):


    def _should_plot_text(self, city_scatter: entities.CityScatter, plot_origins: bool, plot_outpatients: bool):
        if city_scatter.origin_or_outpatient == 'origin' and not plot_origins:
            return False
        elif city_scatter.origin_or_outpatient == 'outpatient' and not plot_outpatients:
            return False
        elif city_scatter.origin_or_outpatient == 'both' and not plot_origins and not plot_outpatients:
            return False
        return True

    def should_plot(self, entity: entities.Entity):
        x=0
