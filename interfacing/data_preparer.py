import pandas as pd


def _apply_count_cities_visiting_providers(row, num_visiting_clinics: dict):
    outpatient_city = row['community']

    if outpatient_city not in num_visiting_clinics:
        num_visiting_clinics[outpatient_city] = 0

    num_visiting_clinics[outpatient_city] += 1


class DataPreparer:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def count_outpatient_visiting_clinics(self):
        num_visiting_clinics = {}
        self.df.apply(_apply_count_cities_visiting_providers, num_visiting_clinics=num_visiting_clinics)
        return num_visiting_clinics

    def get_top_volume_incoming_cities(self, num_results: int):
        counts_dict = self.count_outpatient_visiting_clinics()
        sorted_dict = dict(sorted(counts_dict.items()))
        top_volumes = list(sorted_dict.keys())[-num_results:]
        top_items = counts_dict[top_volumes]
        return top_items

