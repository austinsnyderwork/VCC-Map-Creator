import matplotlib.pyplot as plt

display_fig_size = (20, 15)
county_line_width = 0.05
fig, ax = plt.subplots(figsize=display_fig_size)
iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                           lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                           llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                           urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                           ax=ax)
iowa_map.drawstates()
iowa_map.drawcounties(linewidth=county_line_width)

line_zorder = 0
scatter_zorder = 2
text_poly_zorder = 1

def string_to_tuple(s):
    # Remove the parentheses and any surrounding whitespace
    s = s.strip("()").strip()

    # Split the string by commas and convert each part to an integer (or float, if needed)
    elements = [float(x) for x in s.split(",")]

    # Return the tuple
    return tuple(elements)


def apply_plot_row(row):
    if row['type'] == 'Line':
        x_data = string_to_tuple(row['line_x_data'])
        y_data = string_to_tuple(row['line_y_data'])
        line = ax.plot(x_data, y_data, color=row['line_color'],
                       linestyle=row['line_linestyle'], linewidth=row['line_linewidth'],
                       zorder=line_zorder)
    elif row['type'] == 'CityScatter':
        coord = string_to_tuple(row['scatter_city_coord'])
        scatter_obj = ax.scatter(coord[0], coord[1], marker=row['scatter_marker'],
                                 color=row['scatter_color'], edgecolor=row['scatter_edgecolor'], s=row['scatter_size'],
                                 label=row['scatter_label'], zorder=scatter_zorder)
    elif row['type'] == 'Best':
        coord = string_to_tuple(row['text_poly_coord'])
        city_text = ax.text(coord[0], coord[1], row['text_city_name'],
                            fontsize=row['text_fontsize'],
                            font=row['text_font'],
                            ha='center',
                            va='center',
                            color=row['text_color'],
                            fontweight=row['text_fontweight'],
                            zorder=text_poly_zorder,
                            bbox=dict(facecolor='white', edgecolor='white', boxstyle='square,pad=0.0'))


dataset.apply(apply_plot_row, axis=1)
plt.draw()
plt.show()
