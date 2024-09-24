from config_manager import ConfigManager
import entities


class PlotConfigurations:

    def __init__(self):
        config_manager = ConfigManager()
        self.algo_show_search_area = config_manager.get_config_value('algo_display.show_search_area_poly', bool)
        algo_show_


class PlotController:

    def _should_plot_text(self, city_scatter: entities.Entity, plot_origins: bool, plot_outpatients: bool):
        if city_scatter.origin_or_outpatient == 'origin' and not plot_origins:
            return False
        elif city_scatter.origin_or_outpatient == 'outpatient' and not plot_outpatients:
            return False
        elif city_scatter.origin_or_outpatient == 'both' and not plot_origins and not plot_outpatients:
            return False
        return True

    def should_plot_on_algorithm(self, entity: entities.Entity, iteration: int = 0):
        if isinstance()

    def should_plot_on_visual(self, entity: entities.Entity, iteration):



class ShowController:

    def __init__(self):
        self.plot_configurer = PlotConfigurations()



    def should_show_on_algorithm(self, entity: entities.Entity, iteration: int = -1):
        if isinstance(entity, entities.CityScatter):
            should_show = self._should_show_scatter(entity, iteration)
        elif isinstance(entity, entities.Line):
            should_show = self._should_show_line(entity, iteration)
        elif isinstance(entity, entities.CityTextBox):


        return should_show

    def _should_show_scatter(self):
        if not self.plot_configurer.algo_show_search_area:
            return False

        return True

    def _should_show_line(self):
        if not self.plot_configurer.algo_show_line:
            return False

        return True

    def _should_show_text_box(self):



    def should_show_on_visual(self, entity: entities.Entity, iteration: int = -1):



