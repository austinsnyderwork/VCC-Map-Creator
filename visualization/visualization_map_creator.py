import configparser
import logging
import matplotlib.pyplot as plt
from mpl_toolkits import basemap

import origin_grouping
from . import visualization_element

logging.basicConfig(level=logging.INFO)
config = configparser.ConfigParser()
config.read('config.ini')


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

    def _plot_point(self, coord: dict, origin_and_outpatient: bool, scatter_size,
                    scatter_label, color: str) -> dict:
        lon, lat = coord[0], coord[1]

        marker = "D" if origin_and_outpatient else "s"
        scatter_obj = self.ax.scatter(lon, lat, marker=marker, color=color, s=scatter_size, label=scatter_label)

        return scatter_obj

    def plot_points(self, scatter_size: float, dual_origin_outpatient: list,
                    origin_groups: dict[str, origin_grouping.OriginGroup]) -> list[visualization_element.VisualizationElement]:
        cities_plotted = []
        point_eles = []
        for origin, origin_group_ in origin_groups.items():
            if origin in cities_plotted:
                continue
            origin_in_oo = True if origin in dual_origin_outpatient else False
            coord = (self.city_coords[origin]['longitude'], self.city_coords[origin]['latitude'])
            origin_data = {
                'coord': coord,
                'color': origin_group_.color,
                'origin_and_outpatient': origin_in_oo,
                'scatter_size': scatter_size,
                'scatter_label': 'Outpatient'
            }

            origin_point = self._plot_point(**origin_data)
            origin_ele = visualization_element.VisualizationElement(element_type='scatter',
                                                                    obj=origin_point,
                                                                    city_name=origin,
                                                                    **origin_data)
            point_eles.append(origin_ele)
            cities_plotted.append(origin)

            for outpatient in origin_group_.outpatients:
                if outpatient in cities_plotted:
                    continue

                outpatient_in_oo = True if outpatient in dual_origin_outpatient else False

                coord = (self.city_coords[outpatient]['longitude'], self.city_coords[outpatient]['latitude'])
                outpatient_data = {
                        'coord': coord,
                        'color': origin_group_.color,
                        'origin_and_outpatient': outpatient_in_oo,
                        'scatter_size': scatter_size,
                        'scatter_label': 'Outpatient'
                    }
                outpatient_point = self._plot_point(**outpatient_data)
                outpatient_ele = visualization_element.VisualizationElement(element_type='scatter',
                                                                            obj=outpatient_point,
                                                                            city_name=outpatient,
                                                                            **outpatient_data)
                point_eles.append(outpatient_ele)

                cities_plotted.append(outpatient)
        return point_eles

    def _plot_line(self, origin: str, outpatient: str, color: str, line_width: int) -> plt.Line2D:
        from_lat = self.city_coords[origin]['latitude']
        from_lon = self.city_coords[origin]['longitude']

        to_lat = self.city_coords[outpatient]['latitude']
        to_lon = self.city_coords[outpatient]['longitude']

        lines = self.ax.plot([to_lon, from_lon], [to_lat, from_lat], color=color, linestyle='-', linewidth=line_width)
        line = lines[0]

        return line

    def plot_lines(self, origin_groups: dict, line_width: int) -> list[visualization_element.VisualizationElement]:
        line_eles = []
        for i, (origin, origin_group_) in enumerate(origin_groups.items()):
            for outpatient in origin_group_.outpatients:
                new_line = self._plot_line(color=origin_group_.color,
                                           origin=origin,
                                           outpatient=outpatient,
                                           line_width=line_width)
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

    def _plot_text(self, city_name, text_box_lon, text_box_lat):
        # We don't want Iowa cities to have the state abbreviation
        city_name = city_name.replace(', IA', '')
        city_text = self.ax.text(text_box_lon, text_box_lat, city_name, fontsize=7, font='Tahoma', ha='center', va='center',
                                 color='black',
                                 fontweight='semibold')
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

    def plot_text_boxes(self, text_box_elements: list[visualization_element.VisualizationElement]):
        for text_box_ele in text_box_elements:
            city_text_box = self._plot_text(city_name=text_box_ele.city_name,
                                            text_box_lon=text_box_ele.coord[0],
                                            text_box_lat=text_box_ele.coord[1])

    def show_map(self, show_pause):
        plt.show(block=False)

        plt.pause(show_pause)
