import os
import pandas as pd


def get_dataframe(file_name: str, sheet_name: str = None, specialties=None):
    project_directory = os.getcwd()
    vcc_file_path = os.path.join(project_directory, f"vcc_maps/{file_name}")
    if 'csv' in vcc_file_path:
        df = pd.read_csv(vcc_file_path)
    else:
        df = pd.read_excel(vcc_file_path, sheet_name)

    if specialties:
        df = df[df['specialty'].isin(specialties)]

    return df




