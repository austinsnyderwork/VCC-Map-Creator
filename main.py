from interfacing import interface

vcc_file_name = "/vcc_joined_data.csv"

interface_ = interface.Interface(vcc_file_name=vcc_file_name, city_name_changes={'Des Moines': ['West Des Moines']})
interface_.create_highest_volume_line_map()



