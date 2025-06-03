import logging
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from mpl_toolkits import basemap

from config_manager import ConfigManager
from visualization_elements import CityScatter, CityTextBox, Intersection, \
    TextBoxFinalist, TextBoxNearbySearchArea, Best, Line, TextBoxScanArea, vis_element_classes


def check_show_display(func):
    def wrapper(self, *args, **kwargs):
        if self.show_display:
            return func(self, *args, **kwargs)
        else:
            logging.info(f"{func.__name__} skipped because self.show_display is False.")
            return

    return wrapper


class AlgorithmPlotter:

    def __init__(self, config: ConfigManager, display_fig_size: tuple, county_line_width: float, show_display: bool, show_pause: float):
        self.config = config
        self.show_display = show_display
        self.show_pause = show_pause

        self.fig, self.ax = None, None
        self.map_plot = None

        if show_display:
            self._create_figure(fig_size=display_fig_size,
                                county_line_width=county_line_width)

        self._default_plot_values = None

        self.remove_polys_by_type = {
            CityTextBox: [CityTextBox, Intersection],
            TextBoxFinalist: [CityTextBox, Intersection, TextBoxFinalist, TextBoxNearbySearchArea],
            Best: [TextBoxFinalist, Intersection, TextBoxFinalist, TextBoxNearbySearchArea]
        }

        self.poly_patches = {
            Best: None,
            TextBoxNearbySearchArea: None,
            CityTextBox: None,
            TextBoxFinalist: None
        }

        plt.ion()

    def _create_figure(self, fig_size, county_line_width):
        self.fig, self.ax = plt.subplots(figsize=fig_size)
        self.ax.set_title("Rtree Polygons")
        self.map_plot = basemap.Basemap(projection='lcc', resolution='i',
                                        lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                                        llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                                        urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                                        ax=self.ax)
        self.map_plot.drawstates()
        self.map_plot.drawcounties(linewidth=county_line_width)
        plt.draw()
        plt.pause(0.1)

        logging.info("Created initial algorithm_plot figure.")

        plt.show(block=False)

    def _configure_config_values(self, vis_element_type, input_dict):
        variable_name_type = {
            CityScatter: 'scatter',
            Line: 'line',
            TextBoxNearbySearchArea: 'nearby_search_poly',
            Intersection: 'intersecting_poly',
            Best: 'best_poly',
            CityTextBox: 'scan_poly',
            TextBoxFinalist: 'poly_finalist',
            TextBoxScanArea: 'scan_area_poly'
        }
        v = variable_name_type[vis_element_type]
        show, color, transparency, immediately_remove, center_view = self.config.get_config_values(
            key='algo_display',
            subkeys=[f"show_{v}", f"{v}_color", f"{v}_transparency", f"immediately_remove_{v}", f"center_view_on_{v}"],
            cast_types=[bool, str, float, bool, bool]
        )
        input_dict[vis_element_type] = {
            'show': show,
            'color': color,
            'edgecolor': color,
            'transparency': transparency,
            'immediately_remove': immediately_remove,
            'center_view': center_view
        }

    @property
    def default_plot_values(self):
        if self._default_plot_values is None:
            self._default_plot_values = {}
            self._configure_config_values(CityScatter, self._default_plot_values)
            self._configure_config_values(Line, self._default_plot_values)
            self._configure_config_values(TextBoxNearbySearchArea, self._default_plot_values)
            self._configure_config_values(Intersection, self._default_plot_values)
            self._configure_config_values(Best, self._default_plot_values)
            self._configure_config_values(Best, self._default_plot_values)
            self._configure_config_values(CityTextBox, self._default_plot_values)
            self._configure_config_values(TextBoxFinalist, self._default_plot_values)
            self._configure_config_values(TextBoxScanArea, self._default_plot_values)

        return self._default_plot_values

    def _get_plot_value(self, vis_element, variable, plot_key):
        default_plot_values = self.default_plot_values[type(vis_element)]
        value = getattr(vis_element, f'{variable}') if hasattr(vis_element, f'{variable}') else default_plot_values[plot_key]
        return value

    @check_show_display
    def plot_element(self, vis_element: vis_element_classes.VisualizationElement, poly_override=None):
        edgecolor = self._get_plot_value(vis_element, f"{attr_prefix}edgecolor", 'color')
        facecolor = self._get_plot_value(vis_element, f"{attr_prefix}facecolor", 'color')
        alpha = self._get_plot_value(vis_element, f"{attr_prefix}transparency", 'transparency')
        center_view = self._get_plot_value(vis_element, f"{attr_prefix}center_view", 'center_view')
        show = self._get_plot_value(vis_element, f"{attr_prefix}show", 'show')
        immediately_remove = self._get_plot_value(vis_element, f"{attr_prefix}immediately_remove", 'immediately_remove')

        logging.info(f"Plotting visualization element: {vis_element}")
        if poly_override:
            polygon_coords = list(poly_override.exterior.coords)
        else:
            polygon_coords = list(vis_element.default_poly.exterior.coords)

        # Create a Polygon patch
        polygon_patch = patches.Polygon(polygon_coords, closed=True, fill=True, edgecolor=edgecolor,
                                        facecolor=facecolor, alpha=alpha)
        self._configure_visual(patch=polygon_patch, polygon_coords=polygon_coords,
                               center_view=center_view, show=show, immediately_remove=immediately_remove)

        return polygon_patch

    def _configure_visual(self, patch, polygon_coords, center_view: bool, show: bool, immediately_remove: bool):
        # Add the polygon patch to the axis
        patch = self.ax.add_patch(patch)

        # Ensure the correct figure is active
        plt.figure(self.fig.number)

        # Set axis limits
        if center_view:
            x_coords, y_coords = zip(*polygon_coords)
            self.ax.set_xlim(min(x_coords) - 200000, max(x_coords) + 200000)
            self.ax.set_ylim(min(y_coords) - 200000, max(y_coords) + 200000)

        # Redraw the figure to update the display
        self.fig.canvas.draw()

        if show:
            # Show only the rtree figure
            plt.show(block=False)

            plt.pause(self.show_pause)

        if immediately_remove:
            patch.remove()

        plt.figure(self.fig.number)

        return patch

    @staticmethod
    def remove_patch_from_map(patch):
        patch.remove()
