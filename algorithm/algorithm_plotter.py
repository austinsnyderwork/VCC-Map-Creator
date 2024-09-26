import configparser
import logging
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits import basemap


config = configparser.ConfigParser()
config.read('config.ini')


class AlgorithmPlotter:

    def __init__(self, show_display: bool):
        self.show_display = show_display
        self.poly_types = {}
        self.fig, self.ax = None, None
        self.iowa_map = None

        display_fig_size = (int(config['display']['fig_size_x']), int(config['display']['fig_size_y']))
        self._create_figure(fig_size=display_fig_size,
                            county_line_width=float(config['display']['county_line_width']))

        self.enabled = True

    def _create_figure(self, fig_size, county_line_width):
        if not self.show_display:
            return

        self.fig, self.ax = plt.subplots(figsize=fig_size)
        self.ax.set_title("Rtree Polygons")
        self.iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                                        lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                                        llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                                        urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                                        ax=self.ax)
        self.iowa_map.drawstates()
        self.iowa_map.drawcounties(linewidth=county_line_width)

        plt.figure(self.fig)

    def add_poly_to_map(self, poly, show_algo, center_view=False, color='blue', transparency: float = 1.0,
                        immediately_remove=False, show_pause: float = 1.0, **kwargs):
        if not self.show_display or not self.enabled:
            return

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

        if show_algo:
            # Show only the rtree figure
            plt.show(block=False)

            plt.pause(show_pause)

        if immediately_remove:
            patch.remove()

        plt.figure(self.fig.number)

        return patch

    @staticmethod
    def remove_patch_from_map(patch):
        patch.remove()
