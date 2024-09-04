import matplotlib.pyplot as plt
from mpl_toolkits import basemap
import pandas as pd


def add_city_coord(row, city_coords):
    community = row['community']
    origin = row['point_of_origin']
    if community not in city_coords:
        city_coords[community] = {
            'latitude': row['to_lat'],
            'longitude': row['to_lon']
        }

    if origin not in city_coords:
        city_coords[origin] = {
            'latitude': row['origin_lat'],
            'longitude': row['origin_lon']
        }


def group_by_origin(row, origins_data: dict):
    origin = row['point_of_origin']
    destination = row['community']
    if origin not in origins_data:
        origins_data[origin] = []

    if destination not in origins_data[origin]:
        origins_data[origin].append(destination)


def plot_line(origin: str, outpatient: str, city_coords: dict):
    from_lat, from_lon = city_coords[origin]
    to_lat, to_lon = city_coords[outpatient]


def create_map(vcc_file_path: str, sheet_name: str = None, specialties: list[str] = None):
    if 'csv' in vcc_file_path:
        dataset = pd.read_csv(vcc_file_path)
    else:
        dataset = pd.read_excel(vcc_file_path, sheet_name)

    df = dataset.copy()
    if specialties:
        df = dataset[dataset['specialty'].isin(specialties)]

    city_coords = {}
    df.apply(add_city_coord, city_coords=city_coords, axis=1)

    origins = {}
    df.apply(group_by_origin, origins_data=origins, axis=1)

    origin_and_outpatient = set()
    for origin, outpatients in origins.items():
        for outpatient in outpatients:
            if outpatient in origins.keys():
                origin_and_outpatient.add(outpatient)

    fig, ax = plt.subplots(figsize=(12, 8))
    iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                               lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                               llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                               urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                               ax=ax)
    iowa_map.drawstates()
    iowa_map.drawcounties(linewidth=0.04)

    to_lons, to_lats = iowa_map(list(df['to_lon']), list(df['to_lat']))
    from_lons, from_lats = iowa_map(list(df['origin_lon']), list(df['origin_lat']))

    colors = ['firebrick', 'green', 'teal', 'royalblue', 'purple', 'olive', 'sienna', 'slategrey', 'navy', 'orange',
              'limegreen', 'brown', 'crimson']
    for i, (origin, outpatients) in enumerate(origins.items()):
        color = colors[i]
        for outpatient in outpatients:
            plot_line(origin, outpatient, city_coords, )

    for to_lon, to_lat, from_lon, from_lat in zip(to_lons, to_lats, from_lons, from_lats):
        ax.plot([to_lon, from_lon], [to_lat, from_lat], color='blue', linestyle='-')

    for city, coord in city_coords.items():
        lon, lat = iowa_map(coord['longitude'], coord['latitude'])
        city_name = city.replace(', IA', '')
        plt.text(lon, lat, city_name, fontsize=7, ha='center', color='blue')

    plt.show()


