from abc import ABC

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib import patches
from shapely import Polygon
from matplotlib.patches import Polygon as MplPolygon

from visual_elements.element_classes import CityScatter, Line, TextBox, VisualElement, TextBoxClassification, SearchAreaClassification


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

    # Set the projection for the axis
    ax.set_extent([-97, -89, 40, 44], crs=ccrs.PlateCarree())
    ax.coastlines(resolution='10m')  # or '50m' or '110m'
    ax.add_feature(cfeature.BORDERS.with_scale('10m'), linewidth=0.5)
    ax.add_feature(cfeature.STATES.with_scale('10m'), linewidth=0.5)
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

    return ax


class MapDisplay:

    def __init__(self,
                 figure_size: tuple,
                 county_line_width: float
                 ):

        self.fig, self.ax = plt.subplots(
            subplot_kw={'projection': ccrs.PlateCarree()},
            figsize=figure_size
        )

        self.ax.set_title("Main")
        _create_iowa_map(self.ax)

        self.show_display()

    def determine_text_box_dimensions(self, text_box: TextBox) -> tuple:
        # Iowa cities should not have their state abbreviation
        city_name = text_box.city_name.replace(', IA', '')

        city_text = self.ax.text(0, 0, city_name,
                                 fontsize=text_box.map_attributes['fontsize'],
                                 fontname=text_box.map_attributes.get('font', None),
                                 ha='center',
                                 va='center',
                                 color='purple',
                                 alpha=0.0,  # invisible but rendered
                                 bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))

        self.fig.canvas.draw()
        bbox_coords = city_text.get_window_extent().transformed(self.ax.transData.inverted())
        city_text.remove()

        width = bbox_coords.xmax - bbox_coords.xmin
        height = bbox_coords.ymax - bbox_coords.ymin

        return width, height

    def plot_element(self, visual_element: VisualElement, *args, **kwargs):
        if isinstance(visual_element, CityScatter):
            patch = self.plot_point(scatter=visual_element)
        elif isinstance(visual_element, Line):
            patch = self.plot_line(line=visual_element)
        elif isinstance(visual_element, TextBox):
            patch = self.plot_text(text_box=visual_element)
        else:
            raise ValueError(f"Unsupported VisualElement type {type(VisualElement)}")

        return patch

    def plot_point(self, scatter: CityScatter, **kwargs):
        att = scatter.map_attributes
        scatter_obj = self.ax.scatter(
            scatter.centroid.lon,
            scatter.centroid.lat,
            marker=att['marker'],
            color=att['color'],
            edgecolor=att['edgecolor'] if "edgecolor" in att else None,
            s=scatter.radius,
            label=att['label'],
            zorder=att['zorder'],
            transform=ccrs.PlateCarree(),
            **kwargs
        )

        return scatter_obj

    def plot_line(self, line: Line) -> plt.Line2D:
        att = line.map_attributes
        line = self.ax.plot(
            line.x_data,
            line.y_data,
            color=att['color'],
            linestyle=att['linestyle'],
            linewidth=att['linewidth'],
            zorder=att['zorder'],
            transform=ccrs.PlateCarree(),
        )

        return line

    def plot_text(self, text_box: TextBox):
        # We don't want Iowa cities to have the state abbreviation
        city_name = text_box.city_name.replace(', IA', '')
        lon, lat = text_box.centroid
        city_text = self.ax.text(
            lon,
            lat,
            city_name,
            fontsize=text_box.map_attributes['fontsize'],
            font=text_box.map_attributes['font'],
            ha='center',
            va='center',
            color=text_box.map_attributes['color'],
            fontweight=text_box.map_attributes['fontweight'],
            zorder=text_box.map_attributes['zorder'],
            transform=ccrs.PlateCarree(),
            bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0')
        )
        return city_text

    @staticmethod
    def show_display():
        plt.draw()
        plt.pause(0.1)
        plt.show(block=False)


class AlgorithmDisplay:
    _removes = {
        TextBoxClassification.SCAN: {
            TextBoxClassification.SCAN,
            TextBoxClassification.INTERSECT
        },
        TextBoxClassification.FINALIST: {
            TextBoxClassification.SCAN,
            TextBoxClassification.INTERSECT,
            TextBoxClassification.FINALIST,
            SearchAreaClassification.SCAN
        },
        TextBoxClassification.BEST: {
            TextBoxClassification.FINALIST,
            TextBoxClassification.INTERSECT,
            SearchAreaClassification.SCAN
        }
    }

    def __init__(self, county_line_width: float, show_pause: float, figure_size: tuple):
        print("Initializing AlgorithmDisplay.")
        self.fig, self.ax = plt.subplots(
            subplot_kw={'projection': ccrs.PlateCarree()},
            figsize=figure_size
        )

        self.ax.set_title("Main")
        _create_iowa_map(self.ax)

        plt.show(block=False)

        self.show_pause = show_pause

        self._patches = {
            CityScatter: dict(),
            TextBox: dict(),
            Line: dict()
        }

        self.show_display()

    def _center_display(self, visual_element: VisualElement, padding_degrees=1):
        # Option 1: Center on centroid
        c = visual_element.polygon.centroid

        # Calculate extent around centroid with padding
        extent = [
            c.x - padding_degrees,
            c.x + padding_degrees,
            c.y - padding_degrees,
            c.y + padding_degrees
        ]

        # Set extent on axis in PlateCarree CRS (longitude/latitude)
        self.ax.set_extent(extent, crs=ccrs.PlateCarree())

    def _plot_scatter(self, scatter: CityScatter):
        att = scatter.algorithm_attributes
        patch = patches.Circle(
            (scatter.centroid.lon, scatter.centroid.lat),
            radius=scatter.radius,
            facecolor=att['facecolor'],
            edgecolor=att['edgecolor'] if 'edgecolor' in att else None
        )

        self.ax.add_patch(patch)

        self._patches[CityScatter][scatter] = patch

        return patch

    def _plot_text(self, text_box: TextBox):
        att = text_box.algorithm_attributes
        patch = patches.Rectangle(
            (text_box.centroid.lon, text_box.centroid.lat),
            text_box.width,
            text_box.height,
            facecolor=att['facecolor'],
            edgecolor=att['edgecolor'] if 'edgecolor' in att else None
        )

        self.ax.add_patch(patch)

        self._patches[TextBox][text_box] = patch

        return patch

    def _plot_line(self, line: Line):
        att = line.algorithm_attributes

        line_patch = self.ax.plot(
            line.x_data,
            line.y_data,
            color=att['color'],
            linewidth=att['linewidth'],
            transform=ccrs.PlateCarree()  # 👈 crucial
        )[0]

        self._patches[Line][line] = line_patch

        return line_patch

    def plot_element(self,
                     visual_element,
                     *args,
                     **kwargs):
        if isinstance(visual_element, CityScatter):
            patch = self._plot_scatter(visual_element)
        elif isinstance(visual_element, TextBox):
            patch = self._plot_text(visual_element)
        elif isinstance(visual_element, Line):
            patch = self._plot_line(visual_element)
        else:
            raise TypeError(f"Unsupported VisualElement type {type(visual_element)} for function plot_element")

        # Set axis limits
        if 'center_view' in kwargs and kwargs['center_view']:
            self._center_display(visual_element=visual_element)

        # Redraw the figure to update the display
        self.fig.canvas.draw()

        if 'show' in kwargs and kwargs['show']:
            # Show only the rtree figure
            plt.show(block=False)

            if 'show_pause' in kwargs and kwargs['show_pause']:
                plt.pause(self.show_pause)

        if 'immediately_remove' in kwargs and kwargs['immediately_remove']:
            patch.remove()

        return patch

    def remove_element(self, visual_element: VisualElement):
        patch = self._patches[type(visual_element)][visual_element]
        patch.remove()

    def show_display(self):
        self.fig.show()
        plt.pause(0.1)
        plt.show(block=False)
