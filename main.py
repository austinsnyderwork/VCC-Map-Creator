import logging

import pandas as pd

from plot_maps.city_origin_volume import CityOriginVolumeConditionsController
from program_management import operations_coordinator
from program_management.power_bi_output_formatter import PowerBiOutputFormatter

logging.basicConfig(level=logging.INFO)

vcc_file_name = "C:/Users/austisnyder/Documents/GitHub/VCC-Map-Creator/vcc_maps/vcc_joined_data.csv"
vcc_df = pd.read_csv(vcc_file_name)

city_name_changes = {
    'Des Moines': ['West Des Moines', 'Ankeny', 'Johnston']
}

interface_ = operations_coordinator.OperationsCoordinator(vcc_df=vcc_df)
visual_elements = interface_.create_map(CityOriginVolumeConditionsController)

pbi_df = PowerBiOutputFormatter().create_df(visual_elements=visual_elements)
pbi_df.to_csv("C:/Users/austisnyder/programming/programming_i_o_files/pbi_output.csv")


