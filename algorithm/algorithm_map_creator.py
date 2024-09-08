import configparser
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits import basemap
from rtree import index

from map_creation import helper_functions
from . import poly_creation

config = configparser.ConfigParser()
config.read('config.ini')


class AlgorithmMapCreator:

    def __init__(self):
        self.rtree_idx = index.Index()

        self.poly_types = {}
        self.fig, self.main = None, None

        self._create_figure()

    def _create_figure(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_title("Rtree Polygons")
        iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                                   lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                                   llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                                   urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                                   ax=self.ax)
        iowa_map.drawstates()
        iowa_map.drawcounties(linewidth=0.04)

        plt.figure(self.fig)

    def plot_lines(self, lines: list):
        for line in lines:
            poly = poly_creation.create_poly(poly_type='line', line=line)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='line poly')
            self.poly_types[poly] = 'line'
            self.add_poly_to_map(poly=poly, show_display=False)

    def plot_scatters(self, point_coords, show_display: bool =False):
        scatter_size = float(config['dimensions']['scatter_size'])
        units_radius_per_1_scatter_size = float(config['dimensions']['units_radius_per_1_scatter_size'])
        for i, point_coord in enumerate(point_coords):
            units_radius = scatter_size * units_radius_per_1_scatter_size
            poly = poly_creation.create_poly(poly_type='scatter', center=point_coord, radius=units_radius)
            helper_functions.verify_poly_validity(poly=poly,
                                                  name='scatter poly')
            self.poly_types[poly] = 'point'
            self.add_poly_to_map(poly=poly, show_display=show_display)

    def add_poly_to_map(self, poly, center_view=True, show_display=True, color='blue', transparency=1.0,
                        immediately_remove=False):
        # Get polygon coordinates
        polygon_coords = list(poly.exterior.coords)

        # Create a Polygon patch
        polygon_patch = patches.Polygon(polygon_coords, closed=True, fill=True, edgecolor=color, facecolor=color,
                                        alpha=transparency)

        # Add the polygon patch to the axis
        patch = self.ax.add_patch(polygon_patch)

        # Ensure the correct figure is active
        plt.figure(self.fig.number)

        # Set axis limits
        if center_view:
            x_coords, y_coords = zip(*polygon_coords)
            self.ax.set_xlim(min(x_coords) - 200000, max(x_coords) + 200000)
            self.ax.set_ylim(min(y_coords) - 200000, max(y_coords) + 200000)

        # Redraw the figure to update the display
        self.fig.canvas.draw()

        if show_display:
            # Show only the rtree figure
            plt.show(block=False)

            display_pause = float(config['matplotlib_display']['display_show_pause'])
            plt.pause(display_pause)

        if immediately_remove:
            patch.remove()

        return patch
