import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath

from visual_elements.attributes_resolver import VisualElementAttributesResolver
from visual_elements.element_classes import (CityScatter, Line, TextBox, VisualElement, TextBoxClassification,
                                             VisualElementClassification)


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

    def __init__(self, show_pause: float, figure_size: tuple, display_zoom_out: int):
        print("Initializing AlgorithmDisplay.")
        self.fig, self.ax = plt.subplots(figsize=figure_size)

        self.ax.set_xlim(-96.64, -90.14)
        self.ax.set_ylim(40.37, 43.50)

        self._display_zoom_out = display_zoom_out

        self.ax.set_title("Main")

        plt.show(block=False)

        self.show_pause = show_pause

        self._city_text_dimensions = dict()
        self._patches = Patches()

        self.show_display()

    def center_display(self, visual_element: VisualElement):
        # Option 1: Center on centroid
        c = visual_element.centroid_coord

        zo = self._display_zoom_out
        # Calculate extent around centroid with padding
        extent = [
            c.lon - zo,
            c.lon + zo,
            c.lat - zo,
            c.lat + zo
        ]

        self.ax.set_xlim(extent[0], extent[1])
        self.ax.set_ylim(extent[2], extent[3])

    def determine_text_box_dimensions(self, text_box: TextBox, classification=None) -> tuple:
        if text_box.city_name in self._city_text_dimensions:
            return self._city_text_dimensions[text_box.city_name]

        algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(
            element=text_box,
            classification=classification
        )

        test_txt = self.ax.text(0, 0,
                                text_box.city_name,
                                fontsize=algo_attributes['fontsize'],
                                fontweight=algo_attributes['fontweight'],
                                ha='center',
                                va='center')
        self.fig.canvas.draw()

        renderer = self.fig.canvas.get_renderer()
        bbox = test_txt.get_window_extent(renderer)

        inverse = self.ax.transData.inverted()
        bbox = bbox.transformed(inverse)

        width = bbox.width
        height = bbox.height

        self._city_text_dimensions[text_box.city_name] = width, height

        return width, height

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

    def _plot_scatter(self, scatter: CityScatter, classification, algo_attributes):
        patch = patches.Circle(
            (scatter.coord.lon, scatter.coord.lat),
            radius=scatter.radius,
            facecolor=algo_attributes['facecolor'],
            edgecolor=algo_attributes.get('edgecolor', None),
            zorder=algo_attributes['zorder']
        )
        self.ax.add_patch(patch)
        self._patches.add_patch(patch, classification)

        return patch

    def _plot_text(self, text_box: TextBox, algo_attributes, classification=None):
        self._remove_patches(text_box, classification)
        # Matplotlib rectangles are drawn from bottom-left corner
        bottom_left_point = (
            text_box.centroid_coord.lon - text_box.width / 2,
            text_box.centroid_coord.lat - text_box.height / 2
        )
        patch = patches.Rectangle(
            bottom_left_point,
            text_box.width,
            text_box.height,
            facecolor=algo_attributes['facecolor'],
            edgecolor=algo_attributes.get('edgecolor', None),
            zorder=algo_attributes['zorder']
        )
        self.ax.add_patch(patch)
        self._patches.add_patch(patch, classification)

        return patch

    def _plot_line(self, line: Line, classification, algo_attributes):
        # Remove Cartopy transform; assume x_data and y_data are already in data coords
        line_patch = self.ax.plot(
            line.x_data,
            line.y_data,
            color=algo_attributes['color'],
            linewidth=algo_attributes['linewidth'],
            zorder=algo_attributes['zorder']
        )[0]

        self._patches.add_patch(line_patch, classification)

        return line_patch

    def plot_element(self,
                     visual_element,
                     classification=None,
                     show_display: bool = True,
                     *args,
                     **kwargs):
        algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(
            element=visual_element,
            classification=classification
        )
        if isinstance(visual_element, CityScatter):
            patch = self._plot_scatter(visual_element,
                                       classification,
                                       algo_attributes)
        elif isinstance(visual_element, TextBox):
            patch = self._plot_text(visual_element,
                                    classification,
                                    algo_attributes)
        elif isinstance(visual_element, Line):
            patch = self._plot_line(visual_element,
                                    classification,
                                    algo_attributes)
        else:
            raise TypeError(f"Unsupported VisualElement type {type(visual_element)} for function plot_element")

        # Set axis limits
        if algo_attributes.center_view:
            self.center_display(visual_element=visual_element)

        # Redraw the figure to update the display
        self.fig.canvas.draw()

        if algo_attributes.show:
            # Show only the rtree figure
            plt.show(block=False)

            if 'show_pause' in kwargs and kwargs['show_pause']:
                plt.pause(self.show_pause)

        if show_display:
            self.show_display()

        if algo_attributes.immediately_remove:
            patch.remove()

        return patch

    def show_display(self, block: bool = False):
        self.fig.show()
        plt.pause(0.1)
        plt.show(block=block)
