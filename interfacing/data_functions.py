import pandas as pd


def _apply_count_cities_visiting_providers(row, num_visiting_clinics: dict):
    visiting_city = row['community']

    if visiting_city not in num_visiting_clinics:
        num_visiting_clinics[visiting_city] = 0

    num_visiting_clinics[visiting_city] += 1


def count_visiting_visiting_clinics(df: pd.DataFrame):
    num_visiting_clinics = {}
    df.apply(_apply_count_cities_visiting_providers, num_visiting_clinics=num_visiting_clinics)
    return num_visiting_clinics


def get_top_volume_incoming_cities(df: pd.DataFrame, num_results: int):
    counts_dict = count_visiting_visiting_clinics(df)
    sorted_dict = dict(sorted(counts_dict.items()))
    top_volumes = list(sorted_dict.keys())[-num_results:]
    top_items = counts_dict[top_volumes]
    return top_items

