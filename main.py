import logging

from program_management import operations_coordinator

vcc_file_name = "/vcc_joined_data.csv"

logging.basicConfig(level=logging.INFO)

interface_ = operations_coordinator.OperationsCoordinator(
    vcc_file_name=vcc_file_name,
    city_name_changes={
        'Des Moines': ['West Des Moines', 'Ankeny', 'Johnston'],
        'Omaha, NE': ['Council Bluffs']
    }
)
"""
interface_.create_highest_volume_line_map(results=6,
                                          output_path="C:/Users/austisnyder/programming/programming_i_o_files/visiting_providers.csv")
"""
interface_.create_number_of_visiting_providers_map(output_path="C:/Users/austisnyder/programming/programming_i_o_files/num_visiting_providers.csv")




