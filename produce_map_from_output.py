import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle, FancyBboxPatch
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


def string_to_tuple(s):
    if isinstance(s, tuple):
        return s
    s = s.strip("()").strip()
    return tuple(float(x) for x in s.split(","))


def apply_plot_row(row, ax, m):
    if row['type'] == 'line':
        x_data = string_to_tuple(row['line_x_data'])
        y_data = string_to_tuple(row['line_y_data'])

        x0, y0 = m(x_data[0], y_data[0])
        x1, y1 = m(x_data[1], y_data[1])

        poly = Polygon([[x0, y0], [x1, y1]],
                       closed=False,
                       linewidth=row['line_linewidth'],
                       edgecolor=row['line_facecolor'],
                       linestyle=row['line_linestyle'],
                       facecolor='none',
                       zorder=line_zorder)
        ax.add_patch(poly)

    elif row['type'] == 'cityscatter':
        lon, lat = string_to_tuple(row['cityscatter_city_coord'])
        x, y = m(lon, lat)

        patch = Circle((x, y),
                       radius=row['cityscatter_size'],
                       facecolor=row['cityscatter_facecolor'],
                       edgecolor=row['cityscatter_edgecolor'],
                       zorder=scatter_zorder)
        ax.add_patch(patch)

    elif row['type'] == 'textbox':
        lon, lat = string_to_tuple(row['textbox_poly_coord'])
        x, y = m(lon, lat)

        bbox_patch = dict(
            boxstyle='square,pad=0.0',
            facecolor='white',
            edgecolor='white'
        )
        ax.text(x, y,
                row['textbox_city_name'],
                fontsize=row['textbox_fontsize'],
                ha='center', va='center',
                color=row['textbox_fontcolor'],
                fontweight=row['textbox_fontweight'],
                bbox=bbox_patch,
                zorder=text_poly_zorder)


# --- Main ---
fig, ax, m = create_iowa_basemap(figsize=(12, 9))

line_zorder = 0
scatter_zorder = 2
text_poly_zorder = 1

# Apply each row in your dataset (assumes pandas DataFrame `dataset`)
dataset.apply(lambda row: apply_plot_row(row, ax, m), axis=1)

ax.set_aspect('equal')
plt.tight_layout()
plt.show()