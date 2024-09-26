import logging
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits import basemap

from things.visualization_elements import visualization_elements


class AlgorithmPlotter:

    def __init__(self, show_display: bool, show_pause: int, display_figure_size: tuple, county_line_width: float):
        self.show_display = show_display
        self.show_pause = show_pause
        self.poly_types = {}
        self.fig, self.ax = None, None
        self.iowa_map = None

        self._create_figure(fig_size=display_figure_size,
                            county_line_width=county_line_width)

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

    def plot_element(self, vis_element: visualization_elements.VisualizationElement):
        polygon_coords = list(vis_element.algorithm_poly.exterior.coords)

        # Create a Polygon patch
        polygon_patch = patches.Polygon(polygon_coords, closed=True, fill=True, edgecolor=vis_element.algorithm_color,
                                        facecolor=vis_element.algorithm_color, alpha=vis_element.algorithm_transparency)
        self._configure_visual(vis_element=vis_element, patch=polygon_patch, polygon_coords=polygon_coords)
        return polygon_patch

    def _configure_visual(self, vis_element: visualization_elements.VisualizationElement, patch, polygon_coords):
        # Add the polygon patch to the axis
        patch = self.ax.add_patch(patch)

        # Ensure the correct figure is active
        plt.figure(self.fig.number)

        # Set axis limits
        if vis_element.algorithm_center_view:
            x_coords, y_coords = zip(*polygon_coords)
            self.ax.set_xlim(min(x_coords) - 200000, max(x_coords) + 200000)
            self.ax.set_ylim(min(y_coords) - 200000, max(y_coords) + 200000)

        # Redraw the figure to update the display
        self.fig.canvas.draw()

        if vis_element.algorithm_show:
            # Show only the rtree figure
            plt.show(block=False)

            plt.pause(self.show_pause)

        if vis_element.algorithm_immediately_remove:
            patch.remove()

        plt.figure(self.fig.number)

        return patch

    @staticmethod
    def remove_patch_from_map(patch):
        patch.remove()
