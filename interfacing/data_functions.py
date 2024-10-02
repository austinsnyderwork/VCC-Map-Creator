import pandas as pd


def _apply_count_leaving_provider_by_city(row, num_leaving_clinics: dict):
    origin_city = row['origin_city']

    if origin_city not in num_leaving_clinics:
        num_leaving_clinics[origin_city] = 0

    num_leaving_clinics[origin_city] += 1


def count_leaving_providers(df: pd.DataFrame):
    num_leaving_clinics = {}
    df.apply(_apply_count_leaving_provider_by_city, num_leaving_clinics=num_leaving_clinics, axis=1)
    return num_leaving_clinics


def get_top_volume_origin_cities(df: pd.DataFrame, num_results: int):
    counts_dict = count_leaving_providers(df)
    sorted_dict = dict(sorted(counts_dict.items(), key=lambda item: item[1]))
    top_cities = list(sorted_dict.keys())[-num_results:]
    return top_cities

