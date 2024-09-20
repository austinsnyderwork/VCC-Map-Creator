import configparser
import logging
import matplotlib.pyplot as plt
from mpl_toolkits import basemap

import origin_grouping
from interfacing import visualization_element
from utils.helper_functions import get_config_value

logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config.read('config.ini')


def _group_exclusive_origin_outpatients(origin_groups: dict, dual_origin_outpatient: list):
    excl_origins = [origin for origin in origin_groups.keys() if origin not in dual_origin_outpatient]
    excl_outpatients = []
    for origin_group in origin_groups.values():
        for outpatient in origin_group.outpatients:
            if outpatient not in dual_origin_outpatient:
                excl_outpatients.append(outpatient)
    return excl_origins, excl_outpatients


class VisualizationMapCreator:

    def __init__(self):
        self.poly_types = {}

        self.iowa_map = None
        self.fig, self.ax = None, None

        self.city_coords = {}

        display_fig_size = (int(config['display']['fig_size_x']), int(config['display']['fig_size_y']))
        self._create_figure(fig_size=display_fig_size,
                            county_line_width=float(config['display']['county_line_width']))

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

    def _plot_point(self, marker: str, coord: dict, scatter_size, scatter_label, color: str, edgecolors: str,
                    zorder: int, **kwargs) -> dict:
        lon, lat = coord[0], coord[1]

        scatter_obj = self.ax.scatter(lon, lat, marker=marker, color=color, edgecolors=edgecolors, s=scatter_size,
                                      label=scatter_label, zorder=zorder)

        return scatter_obj

    def plot_points(self, scatter_size: float, dual_origin_outpatients: list,
                    origin_groups: dict[str, origin_grouping.OriginGroup],
                    zorder: int) -> list[visualization_element.VisualizationElement]:
        origin_marker = get_config_value(config, 'display.origin_marker', cast_type=str)
        origin_color = get_config_value(config, 'display.origin_color', cast_type=str)
        outpatient_marker = get_config_value(config, 'display.outpatient_marker', cast_type=str)
        outpatient_color = get_config_value(config, 'display.outpatient_color', cast_type=str)
        dual_origin_outpatient_marker = get_config_value(config, 'display.dual_origin_outpatient_marker', cast_type=str)
        dual_origin_outpatient_color = get_config_value(config, 'display.dual_origin_outpatient_color', cast_type=str)
        dual_origin_outpatient_outer_color = get_config_value(config, 'display.dual_origin_outpatient_outer_color', str)

        excl_origins, excl_outpatients = _group_exclusive_origin_outpatients(origin_groups, dual_origin_outpatients)

        point_eles = []
        for origin in excl_origins:
            coord = (self.city_coords[origin]['longitude'], self.city_coords[origin]['latitude'])
            ooo = 'origin' if origin in excl_origins else 'both'
            origin_data = {
                'coord': coord,
                'scatter_size': scatter_size,
                'scatter_label': 'Origin',
                'origin_or_outpatient': ooo
            }

            marker = origin_marker if origin in excl_origins else dual_origin_outpatient_marker
            color = origin_color if origin in excl_origins else dual_origin_outpatient_color
            edgecolor = origin_color if origin in excl_origins else dual_origin_outpatient_outer_color

            origin_point = self._plot_point(marker=marker,
                                            color=color,
                                            edgecolors=edgecolor,
                                            zorder=zorder,
                                            **origin_data)
            origin_ele = visualization_element.VisualizationElement(element_type='scatter',
                                                                    obj=origin_point,
                                                                    city_name=origin,
                                                                    **origin_data)
            point_eles.append(origin_ele)

            outpatients = origin_groups[origin].outpatients
            for outpatient in outpatients:
                if outpatient in origin_groups:
                    continue

                coord = (self.city_coords[outpatient]['longitude'], self.city_coords[outpatient]['latitude'])

                ooo = 'outpatient' if origin in excl_origins else 'both'
                outpatient_data = {
                    'coord': coord,
                    'scatter_size': scatter_size,
                    'scatter_label': 'Outpatient',
                    'origin_or_outpatient': ooo
                }
                marker = outpatient_marker if outpatient in excl_outpatients else dual_origin_outpatient_marker
                color = outpatient_color if outpatient in excl_outpatients else dual_origin_outpatient_color
                edgecolor = outpatient_color if outpatient in excl_outpatients else dual_origin_outpatient_outer_color

                outpatient_point = self._plot_point(marker=marker,
                                                    color=color,
                                                    edgecolors=edgecolor,
                                                    zorder=zorder,
                                                    **outpatient_data)
                outpatient_ele = visualization_element.VisualizationElement(element_type='scatter',
                                                                            obj=outpatient_point,
                                                                            city_name=outpatient,
                                                                            **outpatient_data)
                point_eles.append(outpatient_ele)
        return point_eles

    def _plot_line(self, origin: str, outpatient: str, color: str, line_width: int, zorder: int) -> plt.Line2D:
        from_lat = self.city_coords[origin]['latitude']
        from_lon = self.city_coords[origin]['longitude']

        to_lat = self.city_coords[outpatient]['latitude']
        to_lon = self.city_coords[outpatient]['longitude']

        lines = self.ax.plot([to_lon, from_lon], [to_lat, from_lat], color=color, linestyle='-', linewidth=line_width,
                             zorder=zorder)
        line = lines[0]

        return line

    def plot_lines(self, origin_groups: dict, line_width: int, zorder: int) -> list[visualization_element.VisualizationElement]:
        line_eles = []
        for i, (origin, origin_group_) in enumerate(origin_groups.items()):
            for outpatient in origin_group_.outpatients:
                new_line = self._plot_line(color=origin_group_.color,
                                           origin=origin,
                                           outpatient=outpatient,
                                           line_width=line_width,
                                           zorder=zorder)
                line_ele = visualization_element.VisualizationElement(element_type='line',
                                                                      obj=new_line,
                                                                      origin=origin,
                                                                      outpatient=outpatient,
                                                                      line_width=line_width,
                                                                      x_data=new_line.get_xdata(),
                                                                      y_data=new_line.get_ydata()
                                                                      )
                line_eles.append(line_ele)
        return line_eles

    def _plot_text(self, city_name: str, text_box_lon: float, text_box_lat: float, zorder: int, fontsize: int,
                   font: str, color: str, fontweight: str):
        # We don't want Iowa cities to have the state abbreviation
        city_name = city_name.replace(', IA', '')
        city_text = self.ax.text(text_box_lon, text_box_lat, city_name, fontsize=fontsize, font=font, ha='center',
                                 va='center',
                                 color=color,
                                 fontweight=fontweight,
                                 zorder=zorder,
                                 bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))
        return city_text

    def get_text_box_dimensions(self, city_name: str, font: str, font_size: int, font_weight: str) -> tuple:
        # We don't want Iowa cities to have the state abbreviation
        city_name = city_name.replace(', IA', '')
        city_text = plt.text(0, 0, city_name, fontsize=font_size, font=font, ha='center', va='center',
                             color='black', fontweight=font_weight)
        self.fig.canvas.draw()
        text_box = city_text.get_window_extent(renderer=self.fig.canvas.get_renderer())

        # Convert from display coordinates to data coordinates
        inverse_coord_obj = self.ax.transData.inverted()
        text_bbox_data = inverse_coord_obj.transform_bbox(text_box)
        x_min, y_min = text_bbox_data.xmin, text_bbox_data.ymin
        x_max, y_max = text_bbox_data.xmax, text_bbox_data.ymax
        text_box_dimensions = {
            'x_min': x_min,
            'y_min': y_min,
            'x_max': x_max,
            'y_max': y_max
        }
        return text_box, text_box_dimensions

    def plot_text_boxes(self, city_elements: list[visualization_element.VisualizationElement], zorder: int):
        fontsize = get_config_value(config, 'viz_display.city_font_size', int)
        font_color = get_config_value(config, 'viz_display.city_font_color', str)
        font_weight = get_config_value(config, 'viz_display.city_font_weight', str)
        font = get_config_value(config, 'viz_display.city_font', str)
        plotted_cities = {}
        for city_ele in city_elements:
            if city_ele.city_name in plotted_cities:
                continue

            logging.info(f"Plotting {city_ele.city_name} text box.")

            text_box_ele = city_ele.text_box_element
            city_text_box = self._plot_text(city_name=city_ele.city_name,
                                            text_box_lon=city_ele.best_poly.centroid.x,
                                            text_box_lat=city_ele.best_poly.centroid.y,
                                            zorder=zorder,
                                            fontsize=fontsize,
                                            color=font_color,
                                            fontweight=font_weight,
                                            font=font)
            text_box_ele.add_value(element='text_box',
                                   value=city_text_box)
            plotted_cities[city_ele.city_name] = city_text_box

    def plot_sample_text_boxes(self, city_elements: list[visualization_element.VisualizationElement]):
        for city_ele in city_elements:
            logging.info(f"Determining text box dimensions for {city_ele.city_name}.")
            # Have to input the text into the map to see its dimensions on our view
            text_box, text_box_dimensions = self.get_text_box_dimensions(
                city_name=city_ele.city_name,
                font=config['viz_display'][
                    'city_font'],
                font_size=int(
                    config['viz_display'][
                        'city_font_size']),
                font_weight=
                config['viz_display'][
                    'city_font_weight'])
            logging.info(f"\tDetermined text box dimensions for {city_ele.city_name}.")
            text_ele = visualization_element.VisualizationElement(element_type='text_box',
                                                                  dimensions=text_box_dimensions)
            city_ele.add_value(element='text_box_element',
                               value=text_ele)

    def show_map(self, show_pause):
        plt.show(block=False)

        plt.pause(show_pause)
