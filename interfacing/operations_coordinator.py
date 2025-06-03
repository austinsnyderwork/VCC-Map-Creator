
import input_output
from . import application_manager
from .power_bi_output_formatter import PowerBiOutputFormatter


class OperationsCoordinator:

    def __init__(self, vcc_file_name: str, city_name_changes: dict, sheet_name: str = None):
        df = input_output.get_dataframe(file_name=vcc_file_name,
                                        sheet_name=sheet_name,
                                        replace_variables={
                                            'visiting_city': city_name_changes,
                                            'origin_city': city_name_changes
                                        })
        self.application_manager = application_manager.ApplicationManager(df=df)
        self.application_manager.startup()

        self.pbif = PowerBiOutputFormatter()

    def create_line_map(self, **kwargs):
        self.application_manager.create_line_map(**kwargs)

    def create_number_of_visiting_providers_map(self, output_path: str, **kwargs):
        vis_elements = self.application_manager.create_number_of_visiting_providers_map(**kwargs)
        self.pbif.add_visualization_elements(vis_elements)
        df = self.pbif.create_df()
        df.to_csv(output_path)

    def create_highest_volume_line_map(self, output_path: str, results: int):
        vis_elements = self.application_manager.create_highest_volume_line_map(number_of_results=results)
        self.pbif.add_visualization_elements(vis_elements)
        df = self.pbif.create_df()
        df.to_csv(output_path)

