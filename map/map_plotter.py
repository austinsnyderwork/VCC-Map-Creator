import logging
import matplotlib.pyplot as plt
from mpl_toolkits import basemap

import config_manager
from things.entities import entities
from things.visualization_elements import visualization_elements


def _group_exclusive_origin_outpatients(origin_groups: dict, dual_origin_outpatient: list):
    excl_origins = [origin for origin in origin_groups.keys() if origin not in dual_origin_outpatient]
    excl_outpatients = []
    for origin_group in origin_groups.values():
        for outpatient in origin_group.outpatients:
            if outpatient not in dual_origin_outpatient:
                excl_outpatients.append(outpatient)
    return excl_origins, excl_outpatients


def show_map(show_pause):
    plt.show(block=False)

    plt.pause(show_pause)


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


class MapPlotter:

    def __init__(self, config_: config_manager.ConfigManager, display_fig_size: tuple, county_line_width: float):
        self.config_ = config_

        self.iowa_map = None
        self.fig, self.ax = None, None

        self._create_figure(fig_size=display_fig_size,
                            county_line_width=county_line_width)

        self.element_plot_funcs = {
            visualization_elements.Line: self._plot_line,
            visualization_elements.CityScatter: self._plot_point,
            visualization_elements.CityTextBox: self._plot_text
        }

    def convert_coord_to_display(self, coord: tuple):
        convert_lon, convert_lat = self.iowa_map(coord)
        return convert_lon, convert_lat

    def _create_figure(self, fig_size, county_line_width: float):
        # Create visual Iowa map
        self.fig, self.ax = plt.subplots(figsize=fig_size)
        self.ax.set_title("Main")
        self.iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                                        lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                                        llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                                        urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                                        ax=self.ax)
        self.iowa_map.drawstates()
        self.iowa_map.drawcounties(linewidth=county_line_width)
        logging.info("Created base Iowa map.")

    def plot_element(self, vis_element: visualization_elements.VisualizationElement, zorder: int):
        func = self.element_plot_funcs[type(vis_element)]
        obj = func(vis_element, zorder)
        return obj

    def _plot_point(self, scatter: visualization_elements.CityScatter, zorder: int, **kwargs):
        scatter_obj = self.ax.scatter(scatter.coord[0], scatter.coord[1], marker=scatter.marker, color=scatter.color,
                                      edgecolor=scatter.edgecolor, s=scatter.size, label=scatter.label, zorder=zorder,
                                      **kwargs)

        return scatter_obj

    def _plot_line(self, line: visualization_elements.Line, zorder: int) -> plt.Line2D:
        line = self.ax.plot(line.x_data, line.y_data, color=line.color, linestyle='-', linewidth=line.linewidth,
                            zorder=zorder)

        return line

    def _plot_text(self, text_box: visualization_elements.CityTextBox, zorder: int):
        # We don't want Iowa cities to have the state abbreviation
        city_name = text_box.city_name.replace(', IA', '')
        lon, lat = text_box.centroid
        city_text = self.ax.text(lon, lat, city_name,
                                 fontsize=text_box.fontsize,
                                 font=text_box.font,
                                 ha='center',
                                 va='center',
                                 color=text_box.color,
                                 fontweight=text_box.fontweight,
                                 zorder=zorder,
                                 bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))
        return city_text

    def get_text_box_dimensions(self, city: entities.City, font_size: int, font: str, font_weight: str) -> dict:
        # We don't want Iowa cities to have the state abbreviation
        city_name = city.name.replace(', IA', '')
        city_text = plt.text(0, 0, city_name, fontsize=font_size, font=font, ha='center', va='center',
                             color='black', fontweight=font_weight)
        self.fig.canvas.draw()
        text_bbox = city_text.get_window_extent(renderer=self.fig.canvas.get_renderer())

        city_text.remove()

        text_box_dimensions = convert_bbox_to_data_coordinates(ax=self.ax,
                                                               bbox=text_bbox)
        return text_box_dimensions
