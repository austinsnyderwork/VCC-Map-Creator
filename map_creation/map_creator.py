import configparser
import itertools
import logging
import matplotlib
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits import basemap
from shapely.geometry import Polygon

from . import helper_functions, origin_group
import input_output

logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config.read('config.ini')


class MapCreator:

    def __init__(self):
        self._create_figures()

        self.origin_groups = {}
        self.city_coords = {}

        self.origin_and_outpatient = []

        self.iowa_map = None
        self.fig_main, self.ax_main = None, None
        self.fig_rtree, self.ax_rtree = None, None

    def _create_figures(self):
        # Create visual Iowa map
        self.fig_main, self.ax_main = plt.subplots(figsize=(12, 8))
        self.ax_main.set_title("Main")
        self.iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                                        lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                                        llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                                        urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                                        ax=self.ax_main)
        self.iowa_map.drawstates()
        self.iowa_map.drawcounties(linewidth=0.04)
        logging.info("Created base Iowa map.")

        # Create algorithm Iowa map
        self.fig_rtree, self.ax_rtree = plt.subplots(figsize=(12, 8))
        self.ax_rtree.set_title("Rtree Polygons")
        iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                                   lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                                   llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                                   urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                                   ax=self.ax_rtree)
        iowa_map.drawstates()
        iowa_map.drawcounties(linewidth=0.04)

        plt.figure(self.fig_main)

    def _add_city_gpd_coord(self, row):
        community = row['community']
        origin = row['point_of_origin']
        if community not in self.city_coords:
            lon, lat = self.iowa_map(row['to_lon'], row['to_lat'])
            self.city_coords[community] = {
                'latitude': lat,
                'longitude': lon
            }

        if origin not in self.city_coords:
            lon, lat = self.iowa_map(row['origin_lon'], row['origin_lat'])
            self.city_coords[origin] = {
                'latitude': lat,
                'longitude': lon
            }

    def _group_by_origin(self, row):
        origin = row['point_of_origin']
        destination = row['community']
        if origin not in self.origin_groups:
            self.origin_groups[origin] = origin_group.OriginGroup(origin=origin)

        self.origin_groups[origin].add_destination(destination)

    def _plot_points(self, ax, origin: str, outpatient: str, origin_coord: tuple, outpatient_coord: tuple,
                     origin_and_outpatient) -> dict:
        from_lon, from_lat = origin_coord[0], origin_coord[1]
        to_lon, to_lat = outpatient_coord[0], outpatient_coord[1]

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

    def _plot_line(self, ax, origin_coord: tuple, outpatient_coord: tuple, color: str) -> plt.Line2D:
        from_lon, from_lat = origin_coord[0], origin_coord[1]
        to_lon, to_lat = outpatient_coord[0], outpatient_coord[1]

        lines = ax.plot([to_lon, from_lon], [to_lat, from_lat], color=color, linestyle='-', linewidth=global_linewidth)
        line = lines[0]

        return line

    def determine_best_poly_group(self, search_polys: dict, intersecting_poly_groups: dict, city_point):
        num_intersections = [len(intersecting_polys) for intersecting_polys in intersecting_poly_groups.values()]
        fewest_intersections = min(num_intersections)
        best_intersections = {intersection_polys: search_poly for intersection_polys, search_poly in
                              intersections_data.items()
                              if len(intersection_polys) == fewest_intersections}

        poly_group_data = {}
        non_text_box_intersections = {}
        for intersecting_polys, search_poly in best_intersections.items():
            data = {}
            poly_group_data[intersecting_polys] = data
            text_box_polys = [poly for poly in intersecting_polys if polygon_types[poly] == 'text_box']
            text_box = True if len(text_box_polys) > 0 else False

            if not text_box:
                non_text_box_intersections[intersecting_polys] = search_poly

        best_distance = 999999999
        best_poly = []
        if len(non_text_box_intersections) > 0:
            for intersecting_polys, search_poly in non_text_box_intersections.items():
                distance = city_point.distance(search_poly)
                if distance < best_distance:
                    best_distance = distance
                    best_poly = search_poly

        return best_poly

    def add_polygon_to_axis(self, poly, set_axis=True, show=True, color='blue', transparency=1.0,
                            immediate_remove=False):
        alg_display = config['matplotlib_display']['should_show_algorithm_display']
        if not alg_display:
            return

        # Get polygon coordinates
        polygon_coords = list(poly.exterior.coords)

        # Create a Polygon patch
        polygon_patch = patches.Polygon(polygon_coords, closed=True, fill=True, edgecolor=color, facecolor=color,
                                        alpha=transparency)

        # Add the polygon patch to the axis
        patch = self.ax_rtree.add_patch(polygon_patch)

        # Ensure the correct figure is active
        plt.figure(self.fig_rtree.number)

        # Set axis limits
        if set_axis:
            x_coords, y_coords = zip(*polygon_coords)
            self.ax_rtree.set_xlim(min(x_coords) - 200000, max(x_coords) + 200000)
            self.ax_rtree.set_ylim(min(y_coords) - 200000, max(y_coords) + 200000)

        # Redraw the figure to update the display
        self.fig_rtree.canvas.draw()

        if show:
            # Show only the rtree figure
            plt.show(block=False)

            display_pause = float(config['matplotlib_display']['display_show_pause'])
            plt.pause(display_pause)

        if immediate_remove:
            patch.remove()

        plt.figure(self.fig_main.number)

        return patch

    def create_map(self, vcc_file_name: str, search_distance_height: float, search_distance_width: float,
                   sheet_name: str = None, specialties: list[str] = None):
        df = input_output.get_dataframe(file_name=vcc_file_name,
                                        sheet_name=sheet_name,
                                        specialties=specialties)

        # Gather necessary city coordinates
        df.apply(self._add_city_gpd_coord, axis=1)
        logging.info("Added city coords.")

        # Group site origins and the respective outpatient clinics associated with them
        df.apply(self._group_by_origin, axis=1)
        logging.info("Grouped by origin.")

        # Find sites that are both an origin and outpatient
        for origin_group in self.origin_groups.values():
            for outpatient in origin_group.outpatients:
                if outpatient in origin_group.keys():
                    self.origin_and_outpatient.append(outpatient)
        logging.info("Found dual origin/outpatient points")

        colors = helper_functions.get_valid_colors()

        logging.info("Plotting lines.")
        lines = []
        for i, (origin, outpatients) in enumerate(origins.items()):
            for outpatient in outpatients:
                new_line = plot_line(ax=ax_main, origin=origin, outpatient=outpatient, city_coords=city_coords,
                                     color=colors[i])
                lines.append(new_line)
        logging.info("\tPlotted lines.")

        logging.info("Creating line polygons for algorithm.")
        for line in lines:
            poly = create_line_polygon(line=line)
            polygon_types[poly] = 'line'
            add_polygon_to_rtree(poly=poly)
            add_polygon_to_axis(poly=poly, show=False)
        logging.info("\tCreated line polygons and inserted into rtree.")

        logging.info("Plotting points.")
        point_coords = []
        for origin, outpatients in origins.items():
            for outpatient in outpatients:
                new_points_dict = plot_points(ax_main, origin, outpatient, city_coords, origin_and_outpatient)
                point_coords.append(new_points_dict['origin'])
                point_coords.append(new_points_dict['outpatient'])
        logging.info("\tPlotted points.")

        logging.info("Creating points polys for algorithm.")
        for i, point_coord in enumerate(point_coords):
            units_radius = global_scatter_size * units_radius_per_1_scatter_size
            poly = create_circle_polygon(center=point_coord, radius=units_radius)
            polygon_types[poly] = 'point'
            add_polygon_to_axis(poly=poly, show=False)
            add_polygon_to_rtree(poly=poly)
        logging.info("\tCreated point polygons and inserted into rtree.")

        num_cities = len(city_coords.values())
        search_area_patch = None
        logging.info("Creating city text.")
        for i, (city, coord) in enumerate(city_coords.items()):
            logging.info(f"\tCreating city text box for {city}.\n\t\t{i} of {num_cities}")
            lon, lat = coord['longitude'], coord['latitude']

            # We don't want Iowa cities to have the state abbreviation
            city_name = city.replace(', IA', '')
            city_text = plt.text(lon, lat, city_name, fontsize=7, font='Tahoma', ha='center', va='center',
                                 color='black',
                                 fontweight='semibold')

            # In this portion of the code, we combine the visual and algorithm portion into one loop. This is because
            # where the text is plotted is dependent on the output of the algorithm
            fig_main.canvas.draw()
            text_bbox = city_text.get_window_extent(renderer=fig_main.canvas.get_renderer())
            # Convert from display coordinates to data coordinates
            inverse_coord_obj = ax_rtree.transData.inverted()
            text_bbox_data = inverse_coord_obj.transform_bbox(text_bbox)
            min_x, min_y = text_bbox_data.xmin, text_bbox_data.ymin
            max_x, max_y = text_bbox_data.xmax, text_bbox_data.ymax
            # min_x, min_y, max_x, max_y = resize_rectangle(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y, factor=2)
            polygon_coords = [
                (min_x, min_y),  # Bottom-left
                (max_x, min_y),  # Bottom-right
                (max_x, max_y),  # Top-right
                (min_x, max_y),  # Top-left
                (min_x, min_y)  # Close the polygon
            ]
            poly = Polygon(polygon_coords)
            if not poly.is_valid:
                raise ValueError("Invalid polygon created from text.")

            search_area_poly = create_search_area_polygon(center_coord=(coord['longitude'], coord['latitude']),
                                                          search_distance_height=search_distance_height,
                                                          search_distance_width=search_distance_width)
            if should_show_algorithm_search_poly:
                search_area_patch = add_polygon_to_axis(poly=search_area_poly,
                                                        color='brown',
                                                        transparency=0.5)
            available_poly = find_available_polygon_around_point(search_poly=poly,
                                                                 search_area_poly=search_area_poly,
                                                                 search_steps=100)
            polygon_types[available_poly] = 'text_box'
            city_text.set_x(available_poly.centroid.x)
            city_text.set_y(available_poly.centroid.y)
            add_polygon_to_axis(poly=available_poly)
            add_polygon_to_rtree(poly=available_poly)

            # If setting to show polygon is off, then there is no patch to remove
            if search_area_patch:
                search_area_patch.remove()
        logging.info("\tCreated city text.")

        plt.show()
