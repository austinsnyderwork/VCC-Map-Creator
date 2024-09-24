import pandas as pd


def _apply_count_outpatient_visiting_clinics(row, num_visiting_clinics: dict):
    origin = row['point_of_origin']
    outpatient = row['community']

    if outpatient not in num_visiting_clinics:
        num_visiting_clinics[outpatient] = {
            'count': 0,
            'visiting_clinics': set()
        }

    if origin not in num_visiting_clinics[outpatient]['visiting_clinics']:
        num_visiting_clinics[outpatient]['count'] += 1
        num_visiting_clinics[outpatient]['visiting_clinics'].add(origin)


class DataPreparer:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def count_outpatient_visiting_clinics(self):
        num_visiting_clinics = {}
        self.df.apply(_apply_count_outpatient_visiting_clinics, num_visiting_clinics=num_visiting_clinics)
        return num_visiting_clinics

