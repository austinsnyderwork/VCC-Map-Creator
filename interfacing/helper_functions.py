
def get_coordinate_from_point(point):
    coordinates = point.get_offsets().tolist()
    coordinate = coordinates[0]
    return coordinate

def determine_search_area_bounds(city_lon, city_lat, search_width: float, search_height: float):
    search_area_bounds = {
        'x_min': city_lon - search_width,
        'y_min': city_lat - search_height,
        'x_max': city_lon + search_width,
        'y_max': city_lat + search_height
    }
    return search_area_bounds



