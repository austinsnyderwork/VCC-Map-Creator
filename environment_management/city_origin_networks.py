import matplotlib

from entities.entity_classes import ProviderAssignment, City
from entities.factory import EntitiesContainer


def _is_dark_color(hex_color):
    # Convert hex to RGB values
    rgb = matplotlib.colors.hex2color(hex_color)
    # Calculate perceived brightness using a common formula
    brightness = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2])
    # A threshold to determine what counts as a "light" color
    return brightness < 0.7


def _fetch_colors():
    all_colors = matplotlib.colors.CSS4_COLORS
    colors = [color for color, hex_value in all_colors.items() if _is_dark_color(hex_value)]
    return colors


class CityNetworksHandler:

    def __init__(self, colors: list[str] = None):
        self.colors = colors or _fetch_colors()
        self._networks = {}

        self.colors_idx = 0

    def _get_color(self):
        color = self.colors[self.colors_idx]
        self.colors_idx += 1
        return color

    def fetch_city_color(self, city: City):
        return self._networks[city]

    def fetch_assignment_color(self, assignment: ProviderAssignment):
        return self._networks[assignment.origin_city]

    def fill_networks(self, entities_container: EntitiesContainer):
        for pa in entities_container.provider_assignments:
            if pa.origin_city in self._networks:
                continue

            self._networks[pa.origin_city] = self._get_color()
