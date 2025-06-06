import logging

import pandas as pd

from plot_maps.city_providers_volume import CityProviderVolumeConditionsController
from plot_maps.highest_volume_cities import HighestOriginVolumeController
from program_management import operations_coordinator

logging.basicConfig(level=logging.INFO)

vcc_file_name = "C:/Users/austisnyder/Documents/GitHub/VCC-Map-Creator/vcc_maps/vcc_joined_data.csv"
vcc_df = pd.read_csv(vcc_file_name)

city_name_changes = {
    'Des Moines': ['West Des Moines', 'Ankeny', 'Johnston'],
    'Omaha, NE': ['Council Bluffs']
}

replacement_map = {
    old_name: new_name
    for new_name, old_names in city_name_changes.items()
    for old_name in old_names
}

vcc_df['visiting_city'] = vcc_df['visiting_city'].replace(replacement_map)
vcc_df['origin_city'] = vcc_df['origin_city'].replace(replacement_map)

interface_ = operations_coordinator.OperationsCoordinator(vcc_df=vcc_df)
interface_.create_map(CityProviderVolumeConditionsController)


