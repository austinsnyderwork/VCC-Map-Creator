import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits import basemap
import pandas as pd


def add_city_gpd_coord(row, plt_map, city_coords):
    community = row['community']
    origin = row['point_of_origin']
    if community not in city_coords:
        lon, lat = plt_map(row['to_lon'], row['to_lat'])
        city_coords[community] = {
            'latitude': lat,
            'longitude': lon
        }

    if origin not in city_coords:
        lon, lat = plt_map(row['origin_lon'], row['origin_lat'])
        city_coords[origin] = {
            'latitude': lat,
            'longitude': lon
        }


def group_by_origin(row, origins_data: dict):
    origin = row['point_of_origin']
    destination = row['community']
    if origin not in origins_data:
        origins_data[origin] = []

    if destination not in origins_data[origin]:
        origins_data[origin].append(destination)


def plot_point(ax, origin: str, outpatient: str, city_coords: dict, origin_and_outpatient):
    from_lat = city_coords[origin]['latitude']
    from_lon = city_coords[origin]['longitude']
    to_lat = city_coords[outpatient]['latitude']
    to_lon = city_coords[outpatient]['longitude']

    origin_marker = "D" if origin in origin_and_outpatient else "s"
    outpatient_marker = "D" if outpatient in origin_and_outpatient else "o"
    ax.scatter(from_lon, from_lat, marker=origin_marker, color='red', s=50, label='Origin')
    ax.scatter(to_lon, to_lat, marker=outpatient_marker, color='blue', s=50, label='Outpatient')


def bboxes_overlap(bbox1, bbox2) -> bool:
    (xmin_1, ymin_1), (xmax_1, ymax_1) = bbox1
    (xmin_2, ymin_2), (xmax_2, ymax_2) = bbox2

    if xmin_1 >= xmax_2 or xmin_2 >= xmax_1:
        return False

    # Check if one rectangle is above the other
    if ymin_1 >= ymax_2 or ymin_2 >= ymax_1:
        return False

    return True

def plot_line(ax, origin: str, outpatient: str, city_coords: dict, color: str):
    from_lat = city_coords[origin]['latitude']
    from_lon = city_coords[origin]['longitude']

    to_lat = city_coords[outpatient]['latitude']
    to_lon = city_coords[outpatient]['longitude']

    lines = ax.plot([to_lon, from_lon], [to_lat, from_lat], color=color, linestyle='-')
    line = lines[0]
    bbox = line.get_path().get_extents()
    x=0


def is_dark_color(hex_color):
    # Convert hex to RGB values
    rgb = matplotlib.colors.hex2color(hex_color)
    # Calculate perceived brightness using a common formula
    brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    # A threshold to determine what counts as a "light" color
    return brightness < 0.7


def create_map(vcc_file_path: str, sheet_name: str = None, specialties: list[str] = None):
    if 'csv' in vcc_file_path:
        dataset = pd.read_csv(vcc_file_path)
    else:
        dataset = pd.read_excel(vcc_file_path, sheet_name)

    df = dataset.copy()
    if specialties:
        df = dataset[dataset['specialty'].isin(specialties)]

    fig, ax = plt.subplots(figsize=(12, 8))
    iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                               lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                               llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                               urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                               ax=ax)
    iowa_map.drawstates()
    iowa_map.drawcounties(linewidth=0.04)

    city_coords = {}
    df.apply(add_city_gpd_coord, city_coords=city_coords, plt_map=iowa_map, axis=1)

    origins = {}
    df.apply(group_by_origin, origins_data=origins, axis=1)

    origin_and_outpatient = set()
    for origin, outpatients in origins.items():
        for outpatient in outpatients:
            if outpatient in origins.keys():
                origin_and_outpatient.add(outpatient)

    all_colors = matplotlib.colors.CSS4_COLORS
    colors = [color for color, hex_value in all_colors.items() if is_dark_color(hex_value)]

    for i, (origin, outpatients) in enumerate(origins.items()):
        for outpatient in outpatients:
            plot_line(ax, origin, outpatient, city_coords, colors[i])

    for origin, outpatients in origins.items():
        for outpatient in outpatients:
            plot_point(ax, origin, outpatient, city_coords, origin_and_outpatient)

    for city, coord in city_coords.items():
        lon, lat = coord['longitude'], coord['latitude']
        city_name = city.replace(', IA', '')
        plt.text(lon, lat, city_name, fontsize=7, font='Tahoma', ha='right', va='top', color='black', fontweight='semibold')

    plt.show()


