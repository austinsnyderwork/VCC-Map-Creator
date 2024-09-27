import input_output
from . import application_manager


class Interface:

    def __init__(self, vcc_file_name: str, city_name_changes: dict, sheet_name: str = None):
        df = input_output.get_dataframe(file_name=vcc_file_name,
                                        sheet_name=sheet_name,
                                        replace_variables={
                                            'visiting_city': city_name_changes,
                                            'origin_city': city_name_changes
                                        })
        self.application_manager = application_manager.ApplicationManager(df=df)

    def create_line_map(self, **kwargs):
        self.application_manager.create_line_map(**kwargs)

    def create_number_of_visiting_providers_map(self, **kwargs):
        self.application_manager.create_number_of_visiting_providers_map(**kwargs)

    def create_highest_volume_line_map(self):
        self.application_manager.create_highest_volume_line_map(number_of_results=4)

