from entities.entity_classes import City, ProviderAssignment
from entities.factory import EntitiesContainer
from environment_management.city_origin_networks import CityNetworksHandler
from plot_maps.base_classes import ConditionsController, ConditionsMap
from visual_elements.element_classes import CityScatter, Line, TextBox


class CityOriginVolumeConditionsController(ConditionsController):

    def __init__(self,
                 entities_container: EntitiesContainer,
                 city_networks_handler: CityNetworksHandler
                 ):
        self._origin_city_volumes = dict()
        self._destination_cities = set()

        self._visual_elements = {
            CityScatter: dict(),
            Line: dict(),
            TextBox: dict()
        }

        cmap = ConditionsMap()
        cmap.add_condition(condition=self._city_condition,
                           entity_type=City)
        cmap.add_condition(condition=self._assignment_condition,
                           entity_type=ProviderAssignment)

        super().__init__(conditions_map=cmap,
                         city_networks_handler=city_networks_handler)

        scatter_thresholds = {
            tuple(range(5, 11)): {
                "radius": 3000,
                "marker": "o",
                "label": "5-10",
                "facecolor": "red",
                "edgecolor": "red",
                "zorder": 3
            },
            tuple(range(11, 16)): {
                "radius": 3000,
                "marker": "o",
                "label": "11-15",
                "facecolor": "blue",
                "edgecolor": "blue",
                "zorder": 3
            },
            tuple(range(16, 21)): {
                "radius": 3000,
                "marker": "o",
                "label": "16-20",
                "facecolor": "orange",
                "edgecolor": "orange",
                "zorder": 3
            },
            tuple(range(21, 1000)): {
                "radius": 3000,
                "marker": "o",
                "label": "21+",
                "facecolor": "black",
                "edgecolor": "black",
                "zorder": 3
            }
        }
        self._scatter_thresholds = {
            k: v
            for k_range, v in scatter_thresholds.items()
            for k in k_range
        }

        self._setup(entities_container=entities_container)

    def _setup(self, entities_container: EntitiesContainer):
        print(f"Setting up {self.__class__.__name__}.")

        # Count the number of leaving providers for each city
        leaving_providers = dict()
        for pa in entities_container.provider_assignments:
            leaving_providers.setdefault(pa.origin_city, set()).add(pa.provider)

        # Count leaving providers from each city, keeping only cities that meet the minimum threshold
        min_leaving_providers = min(self._scatter_thresholds)
        self._origin_city_volumes = {c: len(providers) for c, providers in leaving_providers.items()
                                     if len(providers) >= min_leaving_providers}

        # Determine which cities are visited from valid origin cities
        self._destination_cities = {
            pa.visiting_city for pa in entities_container.provider_assignments
            if pa.origin_city in self._origin_city_volumes
        }

    def _city_condition(self, city: City) -> list:
        ves = []
        if city in self._origin_city_volumes:
            leaving_providers = self._origin_city_volumes[city]
            data = self._scatter_thresholds[leaving_providers]

            city_name = f"{city.city_name}, {self._origin_city_volumes[city]}"
            city_scatter = CityScatter(
                **data,
                coord=city.city_coord,
                city_name=city_name
            )

            # Check if it's a dual-origin/visiting city
            if city in self._destination_cities:
                city_scatter.map_attributes.edgecolor = 'red'

            text_box = TextBox(
                city_name=city_name,
                centroid_coord=city.city_coord,
                font="Roboto",
                fontsize=7,
                fontweight='bold',
                fontcolor="black",
                zorder=2
            )

            ves = [city_scatter, text_box]

        elif city in self._destination_cities:
            city_scatter = CityScatter(
                radius=3000,
                coord=city.city_coord,
                facecolor="black",
                edgecolor="black",
                marker="o",
                label=None,
                city_name=city.city_name
            )
            text_box = TextBox(
                city_name=city.city_name,
                centroid_coord=city.city_coord,
                font="Roboto",
                fontsize=7,
                fontweight='bold',
                fontcolor="black",
                zorder=2
            )

            ves = [city_scatter, text_box]

        returnables = []
        for ve in ves:
            existing = self._visual_elements[type(ve)].get(ve, ve)
            returnables.append(existing)
            self._visual_elements[type(ve)][ve] = ve

        return returnables

    def _assignment_condition(self, pa: ProviderAssignment) -> list:
        if pa.origin_city not in self._origin_city_volumes:
            return []

        line_color = self._city_networks_handler.fetch_city_color(pa.origin_city)

        leaving_providers = self._origin_city_volumes[pa.origin_city]
        if leaving_providers < min(self._scatter_thresholds):
            return []

        line = Line(
            origin_city=pa.origin_city.city_name,
            visiting_city=pa.visiting_city.city_name,
            linewidth=1000,
            facecolor=line_color,
            linestyle="-",
            zorder=1,
            origin_coordinate=pa.origin_city.city_coord,
            visiting_coordinate=pa.visiting_city.city_coord
        )

        existing = self._visual_elements[Line].get(line, line)
        self._visual_elements[Line][existing] = existing
        return [existing]

