import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 9))  # Use a basic figure, no projections

line_zorder = 0
scatter_zorder = 2
text_poly_zorder = 1


def string_to_tuple(s):
    if isinstance(s, tuple):
        return s

    s = s.strip("()").strip()
    return tuple(float(x) for x in s.split(","))


def apply_plot_row(row):
    if row['type'] == 'line':
        x_data = string_to_tuple(row['line_x_data'])
        y_data = string_to_tuple(row['line_y_data'])
        ax.plot(x_data, y_data,
                color=row['line_facecolor'],
                linestyle=row['line_linestyle'],
                linewidth=row['line_linewidth'],
                zorder=line_zorder)

    elif row['type'] == 'cityscatter':
        coord = string_to_tuple(row['cityscatter_city_coord'])
        print(type(coord))
        ax.scatter(coord[0], coord[1],
                   marker=row['cityscatter_marker'],
                   color=row['cityscatter_facecolor'],
                   edgecolor=row['cityscatter_edgecolor'],
                   s=row['cityscatter_size'],
                   label=row['cityscatter_label'],
                   zorder=scatter_zorder)

    elif row['type'] == 'textbox':
        coord = string_to_tuple(row['textbox_poly_coord'])
        ax.text(coord[0], coord[1],
                row['textbox_city_name'],
                fontsize=row['textbox_fontsize'],
                ha='center', va='center',
                color=row['textbox_fontcolor'],
                fontweight=row['textbox_fontweight'],
                zorder=text_poly_zorder,
                bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))


dataset.apply(apply_plot_row, axis=1)

ax.set_aspect('equal')  # Optional: preserve spatial scale
plt.tight_layout()
plt.show()