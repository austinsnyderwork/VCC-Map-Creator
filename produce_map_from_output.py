import ast
from array import array

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import patches
from mpl_toolkits.basemap import Basemap


def create_iowa_basemap(figsize):
    fig, ax = plt.subplots(figsize=figsize)

    m = Basemap(
        projection='lcc',
        resolution='i',
        lat_0=42.0,
        lon_0=-93.5,
        width=700000,
        height=500000,
        ax=ax
    )

    x_min, y_min = m(-97, 40)
    x_max, y_max = m(-90, 44)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    m.drawcoastlines()
    m.drawcountries()
    m.drawstates()
    m.drawcounties()

    return fig, ax, m


def parse_array_string(s: str):
    if isinstance(s, array):  # already parsed
        return s
    return eval(s, {"array": array})


def apply_plot_row(row, ax):
    if row['type'] == 'line':
        x_data = parse_array_string(row['line_x_data'])
        y_data = parse_array_string(row['line_y_data'])

        # print(f"Plotting Line at X_data: {x_data}\n\tY_data: {y_data}")

        patch = patches.Polygon(xy=list(zip(x_data, y_data)),
                                closed=True,
                                facecolor=row['line_facecolor'])
        ax.add_patch(patch)

    elif row['type'] == 'cityscatter':
        lon, lat = ast.literal_eval(row['cityscatter_city_coord'])
        x, y = lon, lat

        # print(f"Plotting CityScatter at ({x}, {y})")

        patch = patches.Circle((x, y),
                               radius=row['cityscatter_size'],
                               facecolor=row['cityscatter_facecolor'],
                               edgecolor=row['cityscatter_edgecolor'],
                               zorder=scatter_zorder)
        ax.add_patch(patch)

    elif row['type'] == 'textbox':
        lon, lat = ast.literal_eval(row['textbox_bottom_left_coord'])

        # print(f"Plotting text at ({lon}, {lat})")

        bbox_patch = dict(
            boxstyle='round,pad=0.0',
            facecolor='white',
            edgecolor='white',
            linewidth=0
        )
        ax.text(lon, lat,
                row['textbox_city_name'],
                fontsize=row['textbox_fontsize'],
                ha='left', va='baseline',
                color=row['textbox_fontcolor'],
                fontweight=row['textbox_fontweight'],
                bbox=bbox_patch,
                zorder=text_poly_zorder)


# --- Main ---
fig, ax, m = create_iowa_basemap(figsize=(12, 9))

line_zorder = 0
scatter_zorder = 2
text_poly_zorder = 1

dataset = pd.read_csv("C:/Users/austisnyder/programming/programming_i_o_files/pbi_output.csv")
# Apply each row in your dataset (assumes pandas DataFrame `dataset`)
dataset.apply(lambda row: apply_plot_row(row, ax), axis=1)

ax.set_aspect('equal')
plt.tight_layout()
plt.show()
