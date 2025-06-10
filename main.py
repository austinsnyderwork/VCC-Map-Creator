import logging

import pandas as pd

from plot_maps.city_providers_volume import CityProviderVolumeConditionsController
from plot_maps.highest_volume_cities import HighestOriginVolumeController
from program_management import operations_coordinator

logging.basicConfig(level=logging.INFO)

vcc_file_name = "C:/Users/austisnyder/Documents/GitHub/VCC-Map-Creator/vcc_maps/vcc_joined_data.csv"
vcc_df = pd.read_csv(vcc_file_name)

city_name_changes = {
    'Des Moines': ['West Des Moines', 'Ankeny', 'Johnston']
}

interface_ = operations_coordinator.OperationsCoordinator(vcc_df=vcc_df)
interface_.create_map(CityProviderVolumeConditionsController)


