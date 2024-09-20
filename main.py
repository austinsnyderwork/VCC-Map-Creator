from interfacing import interface

vcc_file_name = "/vcc_joined_data.csv"

interface_ = interface.Interface()
interface_.import_data(vcc_file_name=vcc_file_name, origins_to_group_together={'Des Moines': ['West Des Moines']})
interface_.create_highest_volume_line_map(num_results=5)



