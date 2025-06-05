import matplotlib.pyplot as plt
from mpl_toolkits import basemap
from visual_elements.element_classes import CityScatter, Line, TextBox

from entities.entity_classes import City
from shared.shared_utils import BoxGeometry


def convert_bbox_to_data_coordinates(ax, bbox):
    inverse_coord_obj = ax.transData.inverted()
    text_bbox_data = inverse_coord_obj.transform_bbox(bbox)
    x_min, y_min = text_bbox_data.xmin, text_bbox_data.ymin
    x_max, y_max = text_bbox_data.xmax, text_bbox_data.ymax
    text_box_dimensions = {
        'x_min': x_min,
        'y_min': y_min,
        'x_max': x_max,
        'y_max': y_max
    }
    return text_box_dimensions


def _create_iowa_map(ax):
    return basemap.Basemap(projection='lcc',
                           resolution='i',
                           lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                           llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                           urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                           ax=ax)


class MapDisplay:

    def __init__(self,
                 figure_size: tuple,
                 county_line_width: float
                 ):
        self.fig, self.ax = plt.subplots(figsize=figure_size)

        self.ax.set_title("Main")

        self.map_plot = _create_iowa_map(self.ax)
        self.map_plot.drawstates()
        self.map_plot.drawcounties(linewidth=county_line_width)

    def convert_coord_to_display(self, coord: tuple):
        lon, lat = coord
        convert_lon, convert_lat = self.map_plot(lon, lat)
        return convert_lon, convert_lat

    def get_text_box_dimensions(self, entity: City, font_size: int, font: str) -> BoxGeometry:
        # Iowa cities should not have their state abbreviation
        city_name = entity.city_name.replace(', IA', '')

        city_text = self.ax.text(0, 0, city_name,
                                 fontsize=font_size,
                                 font=font,
                                 ha='center',
                                 va='center',
                                 color='purple',
                                 visible=False,
                                 bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))

        self.fig.canvas.draw()
        bbox_coords = city_text.get_window_extent().transformed(self.ax.transData.inverted())
        city_text.remove()

        return BoxGeometry(
            x_min=bbox_coords.xmin,
            x_max=bbox_coords.xmax,
            y_min=bbox_coords.ymin,
            y_max=bbox_coords.ymax
        )

    def plot_point(self, scatter: CityScatter, zorder: int, **kwargs):
        scatter_obj = self.ax.scatter(scatter.city_coord[0], scatter.city_coord[1], marker=scatter.marker, color=scatter.color,
                                      edgecolor=scatter.edgecolor, s=scatter.size, label=scatter.label, zorder=zorder,
                                      **kwargs)

        return scatter_obj

    def plot_line(self, line: Line, zorder: int) -> plt.Line2D:
        line = self.ax.attempt_plot(line.x_data, line.y_data, color=line.color, linestyle='-', linewidth=line.linewidth,
                                    zorder=zorder)

        return line

    def plot_text(self,
                  text_box: TextBox,
                  zorder: int
                  ):
        # We don't want Iowa cities to have the state abbreviation
        city_name = text_box.city_name.replace(', IA', '')
        lon, lat = text_box.centroid
        city_text = self.ax.text(lon, lat, city_name,
                                 fontsize=text_box.map_fontsize,
                                 font=text_box.map_font,
                                 ha='center',
                                 va='center',
                                 color=text_box.map_color,
                                 fontweight=text_box.map_fontweight,
                                 zorder=zorder,
                                 bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))
        return city_text

    def plot_element(self,
                     vis_element,
                     zorder: int,
                     override_coord: tuple = None
                     ):
        if isinstance(vis_element, CityScatter):
            self._plot_point()
        plot_func = self.visual_element_plot_funcs[type(vis_element)]
        obj = plot_func(vis_element, zorder, override_coord=override_coord)
        plt.draw()
        if self.show_display:
            plt.pause(0.1)
            plt.show(block=False)
        return obj
