import map_creation

vcc_file_name = "/vcc_joined_data.csv"

map_creation.create_map(vcc_file_name=vcc_file_name, specialties=['Ophthalmology'], search_distance_width=25000,
                        search_distance_height=15000)


