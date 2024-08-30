import geopandas as gpd
import geopy as gp
import logging
import matplotlib.pyplot as plt
import pandas as pd
from shapely.geometry import Point, LineString

logging.basicConfig(level=logging.INFO)

vcc_file_path = "C:/Users/austisnyder/programming/programming_i_o_files/VccDump.xls"
vcc_df = pd.read_excel(vcc_file_path, sheet_name='VccExcelDump')

to_cities = set(vcc_df['Community'])
from_cities = set(vcc_df['Point of Origin'])

from_cities_unique = from_cities - to_cities
to_cities.update(from_cities_unique)
cities = list(to_cities)

gn = gp.geocoders.GeoNames(username='austinsnyder')
city_coords = {}
for city in cities:
    logging.info(f"Geocoding city: {city}")

    # There's a comma if the state abbreviation is already included in the city name (ex: Omaha, NE)
    city_name = city if ',' in city else f"{city}, IA"

    location = gn.geocode(city_name, timeout=10)
    city_coords[city] = location.latitude, location.longitude

row_header = ['city', 'latitude_from', 'longitude_from', 'to', 'latitude_to', 'longitude_to']


def create_power_bi_row(row):
    new_row = pd.Series([''] * len(row_header), index=row_header)
    from_coord = city_coords[row['Point of Origin']]
    to_coord = city_coords[row['Community']]

    new_row['city'] = row['Point of Origin']
    new_row['latitude_from'] = from_coord[0]
    new_row['longitude_from'] = from_coord[1]
    new_row['to'] = row['Community']
    new_row['latitude_to'] = to_coord[0]
    new_row['longitude_to'] = to_coord[1]

    return new_row


power_bi_df = vcc_df.apply(create_power_bi_row, axis=1)
line_color = 'red'

gdf = gpd.GeoDataFrame(power_bi_df, geometry=power_bi_df.apply(
    lambda row: LineString([(row['longitude_from'], row['latitude_from']),
                            (row['longitude_to'], row['latitude_to'])]), axis=1
))

# Define a color map
norm = plt.Normalize(vmin=power_bi_df['Count'].min(), vmax=power_bi_df['Count'].max())
cmap = plt.get_cmap('autumn')

# Plot
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ax = world.plot(figsize=(10, 10), color='white', edgecolor='black')

for idx, row in gdf.iterrows():
    color = cmap(norm(row['Count']))
    x, y = row['geometry'].xy
    ax.plot(x, y, color=color, linewidth=1.5)

plt.show()


