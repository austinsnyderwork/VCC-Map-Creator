import os
import pandas as pd


def get_dataframe(file_name: str, sheet_name: str = None, replace_variables: dict = None):
    project_directory = os.getcwd()
    vcc_file_path = os.path.join(project_directory, f"vcc_maps/{file_name}")
    if 'csv' in vcc_file_path:
        df = pd.read_csv(vcc_file_path)
    else:
        df = pd.read_excel(vcc_file_path, sheet_name)

    if replace_variables:
        for col_name, replace_dict in replace_variables.items():
            for variable, replace_values in replace_dict.items():
                df[col_name] = df[col_name].replace(to_replace=replace_values, value=variable)

    return df




