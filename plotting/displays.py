import pprint

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import patches

from visual_elements.attributes_resolver import VisualElementAttributesResolver
from visual_elements.element_classes import CityScatter, Line, TextBox, VisualElement, AlgorithmClassification


class Patches:

    def __init__(self):
        self._patches = dict()

    def add_patch(self, new_patch, classification):
        if not classification:
            return

        if classification not in self._patches:
            self._patches[classification] = []

        self._patches[classification].append(new_patch)

    def remove_patches(self, classifications):
        patches = [
            p
            for classification, ps in self._patches.items()
            if classification in classifications
            for p in ps
        ]
        removed_dict = {c: [] for c in classifications}
        self._patches.update(removed_dict)

        for patch in patches:
            try:
                patch.remove()
            except (ValueError, NotImplementedError) as e:
                print(f"Warning: failed to remove patch {patch}: {e}")


class AlgorithmDisplay:
    _removes = {
        TextBox: {
            AlgorithmClassification.TEXT_SCAN: {
                AlgorithmClassification.TEXT_SCAN,
                AlgorithmClassification.INTERSECT
            },
            AlgorithmClassification.TEXT_FINALIST: {
                AlgorithmClassification.TEXT_SCAN,
                AlgorithmClassification.INTERSECT,
                AlgorithmClassification.TEXT_FINALIST
            },
            AlgorithmClassification.TEXT_BEST: {
                AlgorithmClassification.TEXT_FINALIST,
                AlgorithmClassification.INTERSECT
            }
        }
    }

    def __init__(self,
                 fig, ax,
                 show_display: bool,
                 show_pause: float,
                 display_zoom_out: float
                 ):
        print("Initializing AlgorithmDisplay.")

        self.fig, self.ax, = fig, ax

        self.show_pause = show_pause

        if show_display:
            plt.draw()
            plt.show(block=False)
            plt.pause(show_pause)

        self._display_zoom_out = display_zoom_out

        self.ax.set_title("Main")

        self._city_text_dimensions = dict()
        self._patches = Patches()

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
        print(f"Centering display on ({c.lon}, {c.lat})\n\tZoom distance: {zo}")

        self.ax.set_xlim(extent[0], extent[1])
        self.ax.set_ylim(extent[2], extent[3])

    def determine_text_box_dimensions(self,
                                      text_box: TextBox,
                                      fontsize: int,
                                      fontweight: str) -> tuple:
        if text_box.city_name in self._city_text_dimensions:
            return self._city_text_dimensions[text_box.city_name]

        test_txt = self.ax.text(0, 0,
                                text_box.city_name,
                                fontsize=fontsize,
                                fontweight=fontweight,
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
        classifications_to_remove = self.__class__._removes.get(type(visual_element), {}).get(classification)
        if not classifications_to_remove:
            return

        self._patches.remove_patches(classifications_to_remove)

    def _plot_scatter(self, scatter: CityScatter, classification, algo_attributes):
        print(f"Plotting CityScatter patch\n\tRadius:{scatter.radius}\n\tZorder: {algo_attributes.zorder}")
        patch = patches.Circle(
            (scatter.coord.lon, scatter.coord.lat),
            radius=scatter.radius,
            facecolor=algo_attributes.facecolor,
            edgecolor=algo_attributes.edgecolor,
            zorder=algo_attributes.zorder
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
        print(f"Plotting TextBox patch\n\tBottom left coord: {bottom_left_point}\n\tWidth: {text_box.width}"
              f"\n\tHeight: {text_box.height}\n\tZorder: {algo_attributes.zorder}")
        patch = patches.Rectangle(
            bottom_left_point,
            text_box.width,
            text_box.height,
            facecolor=algo_attributes.facecolor,
            edgecolor=algo_attributes.edgecolor,
            zorder=algo_attributes.zorder
        )
        self.ax.add_patch(patch)
        self._patches.add_patch(patch, classification)

        return patch

    def _plot_line(self, line: Line, classification, algo_attributes):
        x, y = line.polygon.exterior.xy

        print(f"Plotting Line patch\n\tX: {x}\n\tY: {y}")
        patch = patches.Polygon(xy=list(zip(x, y)),
                                closed=True,
                                facecolor=algo_attributes.facecolor,
                                alpha=algo_attributes.transparency)
        self.ax.add_patch(patch)

        self._patches.add_patch(patch, classification)

        return patch

    def plot_element(self,
                     visual_element,
                     classification,
                     show_display: bool,
                     *args,
                     **kwargs):
        algo_attributes = VisualElementAttributesResolver.resolve_algo_attributes(
            element=visual_element,
            classification=classification
        )
        if isinstance(visual_element, CityScatter):
            patch = self._plot_scatter(visual_element,
                                       algo_attributes=algo_attributes,
                                       classification=classification)
        elif isinstance(visual_element, TextBox):
            patch = self._plot_text(visual_element,
                                    algo_attributes=algo_attributes,
                                    classification=classification)
        elif isinstance(visual_element, Line):
            patch = self._plot_line(visual_element,
                                    algo_attributes=algo_attributes,
                                    classification=classification)
        else:
            raise TypeError(f"Unsupported VisualElement type {type(visual_element)} for function plot_element")

        # Set axis limits
        if algo_attributes.center_view:
            self.center_display(visual_element=visual_element)

        # Redraw the figure to update the display
        self.fig.canvas.draw()

        if show_display and algo_attributes.show:
            self.fig.canvas.draw()
            plt.show(block=False)
            plt.pause(self.show_pause)

        if algo_attributes.immediately_remove:
            patch.remove()

        return patch
