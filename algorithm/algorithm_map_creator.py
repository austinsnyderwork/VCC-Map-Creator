import configparser
from matplotlib import patches
import matplotlib.pyplot as plt
from mpl_toolkits import basemap
from shapely.geometry import Polygon

import poly_creation

config = configparser.ConfigParser()
config.read('config.ini')


class AlgorithmMapCreator:

    def __init__(self):
        self.poly_types = {}
        self.fig, self.ax = None, None
        self.iowa_map = None

        self._create_figure()

    def _create_figure(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.ax.set_title("Rtree Polygons")
        self.iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                                        lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                                        llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                                        urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                                        ax=self.ax)
        self.iowa_map.drawstates()
        self.iowa_map.drawcounties(linewidth=0.04)

        plt.figure(self.fig)

    def _convert_poly_to_display_coordinates(self, poly: Polygon):
        x_min, y_min, x_max, y_max = poly.bounds
        x_min, y_min = self.iowa_map(x_min, y_min)
        x_max, y_max = self.iowa_map(x_max, y_max)
        poly = poly_creation.create_poly(poly_type='rectangle', x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max)
        return poly

    def add_poly_to_map(self, poly, center_view=False, show_display=True, color='blue', transparency=1.0,
                        immediately_remove=False):

        poly = self._convert_poly_to_display_coordinates(poly=poly)

        # Create a Polygon patch
        self.ax.fill(poly)

        # Ensure the correct figure is active
        plt.figure(self.fig.number)

        # Set axis limits
        if center_view:
            x_coords, y_coords = zip(poly.centroid.x, poly.centroid.y)
            self.ax.set_xlim(min(x_coords) - 200000, max(x_coords) + 200000)
            self.ax.set_ylim(min(y_coords) - 200000, max(y_coords) + 200000)

        # Redraw the figure to update the display
        self.fig.canvas.draw()

        if show_display:
            # Show only the rtree figure
            plt.show(block=False)

            display_pause = float(config['algo_display']['show_pause'])
            plt.pause(display_pause)

        if immediately_remove:
            patch.remove()

        return patch
