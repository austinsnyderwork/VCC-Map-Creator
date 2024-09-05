import matplotlib.pyplot as plt
from mpl_toolkits import basemap

delta = 4725
scatter_size = 100

# Central coordinate
central_lat = 270000.0
central_lon = 300000.0

# Define the line coordinates
line_length = 8000
line_lon = [central_lon - (line_length / 2), central_lon + (line_length / 2)]
line_lat = central_lat

# Point above the line
point_above_lat = central_lat + delta
point_below_lat = central_lat - delta

# Plotting
fig, ax = plt.subplots(figsize=(12, 8))
iowa_map = basemap.Basemap(projection='lcc', resolution='i',
                           lat_0=41.5, lon_0=-93.5,  # Central latitude and longitude
                           llcrnrlon=-97, llcrnrlat=40,  # Lower-left corner
                           urcrnrlon=-89, urcrnrlat=44,  # Upper-right corner
                           ax=ax)
iowa_map.drawstates()
iowa_map.drawcounties(linewidth=0.04)

# plt.plot(line_lon, line_lat, 'b-', linewidth=10, label='Horizontal Line')  # Horizontal line
plt.scatter(central_lon, central_lat, color='red', marker='o', s=scatter_size)

plt.scatter(central_lon, point_above_lat, color='black', s=10, marker='o', label='Point Above')       # Point above

# Plot details
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Horizontal Line with Points Above and Below')
plt.legend()
plt.grid(True)
plt.show()


