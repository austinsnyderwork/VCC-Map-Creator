from abc import ABC

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib import patches
from shapely import Polygon
from matplotlib.patches import Polygon as MplPolygon

from plotting.visual_attributes_resolver import VisualElementAttributesResolver
from visual_elements.element_classes import (CityScatter, Line, TextBox, VisualElement, TextBoxClassification,
                                             VisualElementClassification)


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
    ax.set_extent([-97, -89, 40, 44], crs=ccrs.UTM(zone=15, southern_hemisphere=False))
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
            subplot_kw={'projection': ccrs.UTM(zone=15, southern_hemisphere=False)},
            figsize=figure_size
        )

        self.ax.set_title("Main")
        _create_iowa_map(self.ax)

        self.show_display()

    def determine_text_box_dimensions(self, text_box: TextBox) -> tuple:
        map_attributes = VisualElementAttributesResolver.resolve_map_attributes(element=text_box)

        # Iowa cities should not have their state abbreviation
        city_name = text_box.city_name.replace(', IA', '')

        city_text = self.ax.text(0, 0, city_name,
                                 fontsize=map_attributes['fontsize'],
                                 fontname=map_attributes.get('font', None),
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
        map_attributes = VisualElementAttributesResolver.resolve_map_attributes(
            element=scatter
        )

        scatter_obj = self.ax.scatter(
            scatter.coord.lon,
            scatter.coord.lat,
            marker=map_attributes['marker'],
            color=map_attributes['color'],
            edgecolor=map_attributes['edgecolor'] if "edgecolor" in map_attributes else None,
            s=scatter.radius,
            label=map_attributes['label'],
            zorder=map_attributes['zorder'],
            transform=ccrs.UTM(zone=15, southern_hemisphere=False),
            **kwargs
        )

        return scatter_obj

    def plot_line(self, line: Line) -> plt.Line2D:
        map_attributes = VisualElementAttributesResolver.resolve_map_attributes(
            element=line
        )

        line = self.ax.plot(
            line.x_data,
            line.y_data,
            color=map_attributes['color'],
            linestyle=map_attributes['linestyle'],
            linewidth=map_attributes['linewidth'],
            zorder=map_attributes['zorder'],
            transform=ccrs.UTM(zone=15, southern_hemisphere=False),
        )

        return line

    def plot_text(self, text_box: TextBox):
        map_attributes = VisualElementAttributesResolver.resolve_map_attributes(
            element=text_box
        )

        # We don't want Iowa cities to have the state abbreviation
        city_name = text_box.city_name.replace(', IA', '')
        lon, lat = text_box.centroid_coord.lon_lat
        city_text = self.ax.text(
            lon,
            lat,
            city_name,
            fontsize=map_attributes['fontsize'],
            font=map_attributes['font'],
            ha='center',
            va='center',
            fontweight=map_attributes['fontweight'],
            zorder=map_attributes['zorder'],
            transform=ccrs.UTM(zone=15, southern_hemisphere=False),
            bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0')
        )
        return city_text

    @staticmethod
    def show_display():
        plt.draw()
        plt.pause(0.1)
        plt.show(block=False)


class Patches:

    def __init__(self):
        self._patches = dict()

    def add_patch(self, new_patch, classification):
        if not classification:
            return

        if classification not in self._patches:
            self._patches[classification] = []

        self._patches[classification].append(new_patch)

    def fetch_patches_for_removal(self, classifications) -> list:
        patches = [
            p
            for classification, ps in self._patches.items()
            if classification in classifications
            for p in ps
        ]
        removed_dict = {c: [] for c in classifications}
        self._patches.update(removed_dict)

        return patches


class AlgorithmDisplay:
    _removes = {
        TextBox: {
            TextBoxClassification.SCAN: {
                TextBoxClassification.SCAN,
                VisualElementClassification.INTERSECT
            },
            TextBoxClassification.FINALIST: {
                TextBoxClassification.SCAN,
                VisualElementClassification.INTERSECT,
                TextBoxClassification.FINALIST
            },
            TextBoxClassification.BEST: {
                TextBoxClassification.FINALIST,
                VisualElementClassification.INTERSECT
            }
        }
    }

    def __init__(self, show_pause: float, figure_size: tuple, county_line_width: float):
        print("Initializing AlgorithmDisplay.")
        self.fig, self.ax = plt.subplots(
            subplot_kw={'projection': ccrs.UTM(zone=15, southern_hemisphere=False)},
            figsize=figure_size
        )

        self.ax.set_title("Main")
        _create_iowa_map(self.ax)

        plt.show(block=False)

        self.show_pause = show_pause

        self._patches = Patches()

        self.show_display()

    def center_display(self, visual_element: VisualElement, padding_degrees=1):
        # Option 1: Center on centroid
        c = visual_element.centroid_coord

        # Calculate extent around centroid with padding
        extent = [
            c.lon - padding_degrees,
            c.lon + padding_degrees,
            c.lat - padding_degrees,
            c.lat + padding_degrees
        ]

        # Set extent on axis in PlateCarree CRS (longitude/latitude)
        self.ax.set_extent(extent, crs=ccrs.UTM(zone=15, southern_hemisphere=False))

    def _remove_patches(self, visual_element, classification=None):
        if not classification:
            return  # Nothing to remove, exit early

        removes = self.__class__._removes
        if type(visual_element) not in removes:
            return  # No removals configured for TextBox

        remove_classifications = removes[type(visual_element)].get(classification)
        if not remove_classifications:
            return  # Nothing to remove for this classification

        patches_to_remove = self._patches.fetch_patches_for_removal(remove_classifications)

        for patch in patches_to_remove:
            patch.remove()

    def _plot_scatter(self,
                      scatter: CityScatter,
                      classification
                      ):
        algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(
            element=scatter,
            classification=classification
        )
        patch = patches.Circle(
            (scatter.coord.lon, scatter.coord.lat),
            radius=scatter.radius,
            facecolor=algo_attributes['facecolor'],
            edgecolor=algo_attributes['edgecolor'] if 'edgecolor' in algo_attributes else None
        )

        self.ax.add_patch(patch)

        self._patches.add_patch(patch, classification)

        return patch

    def _plot_text(self,
                   text_box: TextBox,
                   classification=None):
        algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(
            element=text_box,
            classification=classification
        )

        self._remove_patches(text_box, classification)

        patch = patches.Rectangle(
            (text_box.centroid_coord.lon, text_box.centroid_coord.lat),
            text_box.width,
            text_box.height,
            facecolor=algo_attributes['facecolor'],
            edgecolor=algo_attributes['edgecolor'] if 'edgecolor' in algo_attributes else None
        )

        self.ax.add_patch(patch)

        self._patches.add_patch(patch, classification)

        return patch

    def _plot_line(self, line: Line, classification):
        algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(
            element=line,
            classification=classification
        )

        line_patch = self.ax.plot(
            line.x_data,
            line.y_data,
            color=algo_attributes['color'],
            linewidth=algo_attributes['linewidth'],
            transform=ccrs.UTM(zone=15, southern_hemisphere=False)  # 👈 crucial
        )[0]

        self._patches.add_patch(line_patch, classification)

        return line_patch

    def plot_element(self,
                     visual_element,
                     classification=None,
                     *args,
                     **kwargs):
        if isinstance(visual_element, CityScatter):
            patch = self._plot_scatter(visual_element, classification)
        elif isinstance(visual_element, TextBox):
            patch = self._plot_text(visual_element, classification)
        elif isinstance(visual_element, Line):
            patch = self._plot_line(visual_element, classification)
        else:
            raise TypeError(f"Unsupported VisualElement type {type(visual_element)} for function plot_element")

        # Set axis limits
        if 'center_view' in kwargs and kwargs['center_view']:
            self.center_display(visual_element=visual_element)

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
