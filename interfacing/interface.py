import input_output
from . import application_manager, plot_controller


def check_data_imported(func):
    def wrapper(self, *args, **kwargs):
        if not self.data_imported:
            raise RuntimeError(f"Have to import data first before calling {__name__}.")
        return func(self, *args, **kwargs)

    return wrapper


class Interface:

    def __init__(self, vcc_file_name: str, city_name_changes: dict, sheet_name: str = None):
        df = input_output.get_dataframe(file_name=vcc_file_name,
                                        sheet_name=sheet_name,
                                        replace_variables={
                                            'community': city_name_changes,
                                            'point_of_origin': city_name_changes
                                        })
        self.application_manager = application_manager.ApplicationManager(df=df)

        self.data_imported = False

    @check_data_imported
    def create_line_map(self, **kwargs):
        self.application_manager.create_line_map(**kwargs)

    @check_data_imported
    def create_number_of_visiting_providers_map(self, **kwargs):
        self.application_manager.create_number_of_visiting_providers_map(**kwargs)

