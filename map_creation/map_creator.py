import geopy as gp
import matplotlib.pyplot as plt
import pandas as pd



vcc_file_path = "C:/Users/austisnyder/programming/programming_i_o_files/VccDump.xls"
vcc_df = pd.read_excel(vcc_file_path, sheet_name='VccExcelDump')

to_cities = set(vcc_df['Community'])
from_cities = set(vcc_df['Point of Origin'])

# Find cities in 'Point of Origin' that are not in 'Community'
from_cities_unique = from_cities - to_cities

# Add unique 'from_cities' to 'to_cities'
to_cities.update(from_cities_unique)

# Convert back to list if needed
to_cities = list(to_cities)
gn = gp.geocoders.GeoNames(username='austinsnyder')
city_coords = {}
for city in cities:
    location = gn.geocode(f"{city}, IA")
    city_coords[city] = location.latitude, location.longitude


