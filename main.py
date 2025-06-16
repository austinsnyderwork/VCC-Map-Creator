import logging

import pandas as pd

from plot_maps.city_origin_volume import CityOriginVolumeConditionsController
from program_management import operations_coordinator
from program_management.power_bi_output_formatter import PowerBiOutputFormatter

logging.basicConfig(level=logging.INFO)


vcc_file_name = "C:/Users/austisnyder/Documents/GitHub/VCC-Map-Creator/vcc_maps/vcc_joined_data.csv"
vcc_df = pd.read_csv(vcc_file_name)

city_name_changes = {
    'West Des Moines': 'Des Moines',
    'Ankeny': 'Des Moines',
    'Johnston': 'Des Moines',
    'Coralville': 'Iowa City',
    'North Liberty': 'Iowa City',
    'Bettendorf': 'Davenport',
    'Clive': 'Urbandale'
}

interface_ = operations_coordinator.OperationsCoordinator(vcc_df=vcc_df, city_name_changes=city_name_changes)
visual_elements = interface_.create_map(CityOriginVolumeConditionsController)

pbi_df = PowerBiOutputFormatter().create_df(visual_elements=visual_elements)
pbi_df.to_csv("C:/Users/austisnyder/programming/programming_i_o_files/pbi_output.csv")


