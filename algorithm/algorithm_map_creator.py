import configparser
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits import basemap


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

    def add_poly_to_map(self, poly, center_view=False, show_display=True, color='blue', transparency=1.0,
                        immediately_remove=False, display_show_pause: float = 1.0):

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

            plt.pause(display_show_pause)

        if immediately_remove:
            patch.remove()

        plt.figure(self.fig.number)

        return patch
