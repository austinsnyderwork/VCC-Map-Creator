import itertools
import logging
import math
import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib import text
from mpl_toolkits import basemap
import numpy as np
import os
import pandas as pd
from rtree import index
import shapely
from shapely.geometry import Polygon, box

logging.basicConfig(level=logging.INFO)

global_linewidth = 2
global_scatter_size = 50
text_box_search_radius = 1000

# Note that the 1 linewidth is how far the border of the line extends to ONE SIDE. So it increases by x units in both
# directions per 1 linewidth
units_per_1_linewidth = 675.0

units_radius_per_1_scatter_size = 50


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


def plot_points(ax, origin: str, outpatient: str, city_coords: dict, origin_and_outpatient) -> dict:
    from_lat = city_coords[origin]['latitude']
    from_lon = city_coords[origin]['longitude']
    to_lat = city_coords[outpatient]['latitude']
    to_lon = city_coords[outpatient]['longitude']

    origin_marker = "D" if origin in origin_and_outpatient else "s"
    outpatient_marker = "D" if outpatient in origin_and_outpatient else "o"
    scatter_origin = ax.scatter(from_lon, from_lat, marker=origin_marker, color='red', s=global_scatter_size,
                                label='Origin')
    scatter_outpatient = ax.scatter(to_lon, to_lat, marker=outpatient_marker, color='blue', s=global_scatter_size,
                                    label='Outpatient')

    return {
        'origin': (from_lon, from_lat),
        'outpatient': (to_lon, to_lat)
    }


def bboxes_overlap(bbox1, bbox2) -> bool:
    (xmin_1, ymin_1), (xmax_1, ymax_1) = bbox1
    (xmin_2, ymin_2), (xmax_2, ymax_2) = bbox2

    if xmin_1 >= xmax_2 or xmin_2 >= xmax_1:
        return False

    # Check if one rectangle is above the other
    if ymin_1 >= ymax_2 or ymin_2 >= ymax_1:
        return False

    return True


def plot_line(ax, origin: str, outpatient: str, city_coords: dict, color: str) -> plt.Line2D:
    from_lat = city_coords[origin]['latitude']
    from_lon = city_coords[origin]['longitude']

    to_lat = city_coords[outpatient]['latitude']
    to_lon = city_coords[outpatient]['longitude']

    lines = ax.plot([to_lon, from_lon], [to_lat, from_lat], color=color, linestyle='-', linewidth=global_linewidth)
    line = lines[0]

    return line


def move_coordinate(x, y, slope, distance):
    angle = math.atan(slope)  # arctan gives the angle from the slope

    # Calculate the change in x and y using the angle and distance
    delta_x = distance * math.cos(angle)  # Adjacent side of the right triangle
    delta_y = distance * math.sin(angle)  # Opposite side of the right triangle

    # Calculate new coordinates
    new_x = x + delta_x
    new_y = y + delta_y

    return new_x, new_y


def create_line_polygon(line: plt.Line2D) -> Polygon:
    line_width = line.get_linewidth()
    x_data = line.get_xdata()
    y_data = line.get_ydata()

    line_coord_0 = (x_data[0], y_data[0])
    line_coord_1 = (x_data[1], y_data[1])

    slope = (y_data[1] - y_data[0]) / (x_data[1] - x_data[0])
    perpendicular_slope = -1 / slope

    poly_coords = []
    for coord in [line_coord_0, line_coord_1]:
        new_coord_0 = move_coordinate(coord[0], coord[1], slope=perpendicular_slope, distance=line_width / 2)
        new_coord_1 = move_coordinate(coord[0], coord[1], slope=-perpendicular_slope, distance=line_width / 2)
        poly_coords.append(new_coord_0)
        poly_coords.append(new_coord_1)

    poly = create_polygon_from_points(points=poly_coords)
    return poly


def create_circle_polygon(center, radius, num_points=100) -> Polygon:
    angles = np.linspace(0, 2 * np.pi, num_points)
    points = [(center[0] + radius * np.cos(angle), center[1] + radius * np.sin(angle)) for angle in angles]
    return Polygon(points)


def get_intersecting_polygons(search_polygon, rtree_idx, polygons) -> list[Polygon]:
    intersection_indices = list(rtree_idx.intersection(search_polygon.bounds))
    interecting_polygons = [polygons[idx] for idx in intersection_indices]
    return interecting_polygons


def create_rectangle_polygon(x_coords, y_coords) -> Polygon:
    coordinates = [
        (x_coords[0], y_coords[0]),  # Bottom-left corner
        (x_coords[1], y_coords[0]),  # Bottom-right corner
        (x_coords[1], y_coords[1]),  # Top-right corner
        (x_coords[0], y_coords[1]),  # Top-left corner
        (x_coords[0], y_coords[0])  # Closing the polygon by returning to the start
    ]

    # Create and return the Polygon
    return Polygon(coordinates)


def create_polygon_from_points(points):
    for permutation in itertools.permutations(points):
        polygon = Polygon(permutation)
        if polygon.is_valid:
            return polygon

    raise ValueError("Could not form a valid polygon with the given points.")


def find_available_polygon_around_point(search_polygon, search_radius, rtree_idx, polygons,
                                        search_steps=100) -> Polygon:
    search_poly_center = search_polygon.centroid
    search_poly_min_x, search_poly_min_y, search_poly_max_x, search_poly_max_y = search_polygon.bounds
    search_poly_x_len = search_poly_max_x - search_poly_min_x
    search_poly_y_len = search_poly_max_y - search_poly_min_y

    search_area = box(
        search_poly_center.x - search_radius,
        search_poly_center.y - search_radius,
        search_poly_center.x + search_radius,
        search_poly_center.y + search_radius
    )
    search_area_min_x, search_area_min_y, search_area_max_x, search_area_max_y = search_area.bounds

    search_area_left_x_coords = (search_area_min_x, search_area_min_x + search_poly_x_len)
    search_area_right_x_coords = (search_area_max_x - search_poly_x_len, search_area_max_x)

    search_area_bottom_y_coords = (search_area_min_y, search_area_min_y + search_poly_y_len)
    search_area_top_y_coords = (search_area_max_y - search_poly_y_len, search_area_max_y)

    polys = []

    best_poly = None
    best_poly_intersections = 100

    bottom_left_poly = create_rectangle_polygon(x_coords=search_area_left_x_coords,
                                                y_coords=search_area_bottom_y_coords)
    polys.append(bottom_left_poly)
    top_left_poly = create_rectangle_polygon(x_coords=search_area_left_x_coords,
                                             y_coords=search_area_top_y_coords)
    polys.append(top_left_poly)
    bottom_right_poly = create_rectangle_polygon(x_coords=search_area_right_x_coords,
                                                 y_coords=search_area_bottom_y_coords)
    polys.append(bottom_right_poly)
    top_right_poly = create_rectangle_polygon(x_coords=search_area_right_x_coords,
                                              y_coords=search_area_top_y_coords)
    polys.append(top_right_poly)

    for poly in polys:
        intersections = get_intersecting_polygons(search_polygon=poly,
                                                  rtree_idx=rtree_idx,
                                                  polygons=polygons)
        if len(intersections) == 0:
            logging.info(f"\t\tFound space for poly.")
            return poly

        if len(intersections) < best_poly_intersections:
            best_poly = poly

    maximum_x_min = search_area_max_x - search_poly_x_len
    min_x_steps = np.linspace(search_area_min_x, maximum_x_min, search_steps)
    # We already try the extreme corners of the search area, so skip those corners in these steps
    min_x_steps = min_x_steps[1:-1]

    maximum_y_min = search_area_max_y - search_poly_y_len
    min_y_steps = np.linspace(search_area_min_y, maximum_y_min, search_steps)
    # We already try the extreme corners of the search area, so skip those corners in these steps
    min_y_steps = min_y_steps[1:-1]

    for min_x in min_x_steps:
        for min_y in min_y_steps:
            max_x = min_x + search_poly_x_len
            max_y = min_y + search_poly_y_len
            poly = create_rectangle_polygon(x_coords=(min_x, max_x),
                                            y_coords=(min_y, max_y))
            intersections = get_intersecting_polygons(search_polygon=poly,
                                                      rtree_idx=rtree_idx,
                                                      polygons=polygons)
            if len(intersections) == 0:
                logging.info(f"\t\tFound space for poly.")
                return poly

            if len(intersections) < best_poly_intersections:
                best_poly = poly

    # If we can't find any polygons with 0 intersections, then just return the one with the least number
    logging.info(f"\t\tCould not find space for poly.")
    return best_poly


def is_dark_color(hex_color):
    # Convert hex to RGB values
    rgb = matplotlib.colors.hex2color(hex_color)
    # Calculate perceived brightness using a common formula
    brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    # A threshold to determine what counts as a "light" color
    return brightness < 0.7


polygons = {}
poly_idx = 0
rtree_idx = index.Index()


def add_polygon_to_rtree(poly: Polygon):
    global poly_idx
    global rtree_idx
    rtree_idx.insert(poly_idx, poly.bounds, obj=poly)
    polygons[poly_idx] = poly
    poly_idx += 1


def add_polygon_to_axis(ax_rtree, fig_rtree, fig_main, poly: Polygon, show=True):
    # Get polygon coordinates
    polygon_coords = list(poly.exterior.coords)

    # Create a Polygon patch
    polygon_patch = patches.Polygon(polygon_coords, closed=True, fill=True, edgecolor='blue', facecolor='cyan')

    # Add the polygon patch to the axis
    ax_rtree.add_patch(polygon_patch)

    # Ensure the correct figure is active
    plt.figure(fig_rtree.number)

    # Set axis limits
    x_coords, y_coords = zip(*polygon_coords)
    ax_rtree.set_xlim(min(x_coords) - 200000, max(x_coords) + 200000)
    ax_rtree.set_ylim(min(y_coords) - 200000, max(y_coords) + 200000)

    # Redraw the figure to update the display
    fig_rtree.canvas.draw()

    if show:
        # Show only the rtree figure
        plt.show(block=False)

        plt.pause(0.1)

    plt.figure(fig_main.number)


def resize_rectangle(min_x, min_y, max_x, max_y, factor):
    # Calculate the center of the original rectangle
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # Calculate the original width and height
    original_width = max_x - min_x
    original_height = max_y - min_y

    # Calculate new width and height based on the given factor
    new_width = original_width / factor
    new_height = original_height / factor

    # Calculate new min and max coordinates
    new_min_x = center_x - new_width / 2
    new_max_x = center_x + new_width / 2
    new_min_y = center_y - new_height / 2
    new_max_y = center_y + new_height / 2

    return new_min_x, new_min_y, new_max_x, new_max_y


def create_map(vcc_file_name: str, sheet_name: str = None, specialties: list[str] = None):
    project_directory = os.getcwd()
    vcc_file_path = os.path.join(project_directory, f"vcc_maps/{vcc_file_name}")
    if 'csv' in vcc_file_path:
        dataset = pd.read_csv(vcc_file_path)
    else:
        dataset = pd.read_excel(vcc_file_path, sheet_name)
    logging.info("Read VCC dataframe.")

    df = dataset.copy()
    if specialties:
        df = dataset[dataset['specialty'].isin(specialties)]

    fig_main, ax_main = plt.subplots(figsize=(12, 8))
    ax_main.set_title("Main")
    iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                               lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                               llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                               urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                               ax=ax_main)
    iowa_map.drawstates()
    iowa_map.drawcounties(linewidth=0.04)
    logging.info("Created base Iowa map.")

    fig_rtree, ax_rtree = plt.subplots(figsize=(12, 8))
    ax_rtree.set_title("Rtree Polygons")
    iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                               lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                               llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                               urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                               ax=ax_rtree)
    iowa_map.drawstates()
    iowa_map.drawcounties(linewidth=0.04)

    plt.figure(fig_main)

    city_coords = {}
    df.apply(add_city_gpd_coord, city_coords=city_coords, plt_map=iowa_map, axis=1)
    logging.info("Added city coords.")

    origins = {}
    df.apply(group_by_origin, origins_data=origins, axis=1)
    logging.info("Grouped by origin.")

    origin_and_outpatient = set()
    for origin, outpatients in origins.items():
        for outpatient in outpatients:
            if outpatient in origins.keys():
                origin_and_outpatient.add(outpatient)
    logging.info("Found dual origin/outpatient points")

    all_colors = matplotlib.colors.CSS4_COLORS
    colors = [color for color, hex_value in all_colors.items() if is_dark_color(hex_value)]

    logging.info("Plotting lines.")

    lines = []
    for i, (origin, outpatients) in enumerate(origins.items()):
        for outpatient in outpatients:
            new_line = plot_line(ax=ax_main, origin=origin, outpatient=outpatient, city_coords=city_coords, color=colors[i])
            lines.append(new_line)
    logging.info("\tPlotted lines.")

    logging.info("Creating line polygons.")
    for line in lines:
        poly = create_line_polygon(line=line)
        add_polygon_to_rtree(poly=poly)
        add_polygon_to_axis(ax_rtree=ax_rtree, fig_rtree=fig_rtree, fig_main=fig_main, poly=poly, show=False)
    logging.info("\tCreated line polygons and inserted into rtree.")

    logging.info("Plotting points.")
    point_coords = []
    for origin, outpatients in origins.items():
        for outpatient in outpatients:
            new_points_dict = plot_points(ax_main, origin, outpatient, city_coords, origin_and_outpatient)
            point_coords.append(new_points_dict['origin'])
            point_coords.append(new_points_dict['outpatient'])
    logging.info("\tPlotted points.")

    logging.info("Creating points polys.")
    for i, point_coord in enumerate(point_coords):
        units_radius = global_scatter_size * units_radius_per_1_scatter_size
        poly = create_circle_polygon(center=point_coord, radius=units_radius)
        add_polygon_to_axis(ax_rtree=ax_rtree, fig_rtree=fig_rtree, fig_main=fig_main, poly=poly, show=False)
        add_polygon_to_rtree(poly=poly)
    logging.info("\tCreated point polygons and inserted into rtree.")

    num_cities = len(city_coords.values())
    logging.info("Creating city text.")
    for i, (city, coord) in enumerate(city_coords.items()):
        logging.info(f"\tCreating city text box for {city}.\n\t\t{i} of {num_cities}")
        lon, lat = coord['longitude'], coord['latitude']
        city_name = city.replace(', IA', '')
        city_text = plt.text(lon, lat, city_name, fontsize=7, font='Tahoma', ha='center', va='center', color='black',
                             fontweight='semibold')
        fig_main.canvas.draw()
        bbox = city_text.get_window_extent(renderer=fig_main.canvas.get_renderer())
        min_x, min_y, width, height = bbox.bounds
        inv = ax_main.transData.inverted()
        text_coords = inv.transform(bbox_coords)
        text_coords = resize_rectangle(min_x=text_coords[0], min_y=text_coords[1], max_x=text_coords[2], max_y=text_coords[3], factor=2)
        polygon_coords = [
            (text_coords[0], text_coords[1]),  # Bottom-left
            (text_coords[0] + text_coords[2], text_coords[1]),  # Bottom-right
            (text_coords[0] + text_coords[2], text_coords[1] + text_coords[3]),  # Top-right
            (text_coords[0], text_coords[1] + text_coords[3]),  # Top-left
        ]
        poly = Polygon(polygon_coords)
        if not poly.is_valid:
            raise ValueError("Invalid polygon created from text.")
        available_poly = find_available_polygon_around_point(search_polygon=poly,
                                                             search_radius=text_box_search_radius,
                                                             rtree_idx=rtree_idx,
                                                             polygons=polygons,
                                                             search_steps=100)
        city_text.set_x(available_poly.centroid.x)
        city_text.set_y(available_poly.centroid.y )
        add_polygon_to_axis(ax_rtree=ax_rtree, fig_rtree=fig_rtree, fig_main=fig_main, poly=available_poly)
        add_polygon_to_rtree(poly=available_poly)
    logging.info("\tCreated city text.")

    plt.show()
