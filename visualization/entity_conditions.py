import configparser

from utils.helper_functions import get_config_value


config = configparser.ConfigParser()
config.read('config.ini')


def range_1_condition(num_visiting_clinics: int, **kwargs):
    range_1_min = get_config_value(config, 'num_visiting_clinics.range_1_min', int)
    range_1_max = get_config_value(config, 'num_visiting_clinics.range_1_max', int)

    if range_1_min < num_visiting_clinics < range_1_max:
        return True

    return False


def range_2_condition(num_visiting_clinics: int, **kwargs):
    range_2_min = get_config_value(config, 'num_visiting_clinics.range_2_min', int)
    range_2_max = get_config_value(config, 'num_visiting_clinics.range_2_max', int)

    if range_2_min < num_visiting_clinics < range_2_max:
        return True

    return False


def range_3_condition(num_visiting_clinics: int, **kwargs):
    range_3_min = get_config_value(config, 'num_visiting_clinics.range_3_min', int)
    range_3_max = get_config_value(config, 'num_visiting_clinics.range_3_max', int)

    if range_3_min < num_visiting_clinics < range_3_max:
        return True

    return False


def range_4_condition(num_visiting_clinics: int, **kwargs):
    range_4_min = get_config_value(config, 'num_visiting_clinics.range_4_min', int)
    range_4_max = 1e5

    if range_4_min < num_visiting_clinics < range_4_max:
        return True

    return False
