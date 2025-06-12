from entities.entity_classes import City, ProviderAssignment
from entities.factory import EntitiesContainer
from environment_management.city_origin_networks import CityNetworksHandler
from plot_maps.base_classes import ConditionsController, ConditionsMap
from visual_elements.element_classes import CityScatter, Line, TextBox, VisualElementAttributes


class CityOriginVolumeConditionsController(ConditionsController):

    def __init__(self,
                 entities_container: EntitiesContainer,
                 city_networks_handler: CityNetworksHandler
                 ):
        self._valid_origin_cities_volume = dict()
        self._destination_cities = set()
        self._line_assignments_created = set()

        cmap = ConditionsMap()
        cmap.add_condition(condition=self._city_condition,
                           entity_type=City)
        cmap.add_condition(condition=self._assignment_condition,
                           entity_type=ProviderAssignment)

        super().__init__(conditions_map=cmap,
                         city_networks_handler=city_networks_handler)

        scatter_thresholds = {
            tuple(range(5, 11)): {
                "radius": 150,
                "marker": "o",
                "label": "5-10",
                "facecolor": "red",
                "edgecolor": "red",
                "zorder": 3
            },
            tuple(range(11, 16)): {
                "radius": 150,
                "marker": "o",
                "label": "11-15",
                "facecolor": "blue",
                "edgecolor": "blue",
                "zorder": 3
            },
            tuple(range(16, 21)): {
                "radius": 150,
                "marker": "o",
                "label": "16-20",
                "facecolor": "orange",
                "edgecolor": "orange",
                "zorder": 3
            },
            tuple(range(21, 1000)): {
                "radius": 150,
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
        leaving_providers = dict()
        destination_cities = dict()

        print(f"Setting up {self.__class__.__name__} EntitiesContainer.")
        for pa in entities_container.provider_assignments:
            if pa.origin_city not in leaving_providers:
                leaving_providers[pa.origin_city] = set()
            leaving_providers[pa.origin_city].add(pa.provider)

            if pa.origin_city not in destination_cities:
                destination_cities[pa.origin_city] = set()
            destination_cities[pa.origin_city].add(pa.visiting_city)

        min_leaving_providers = min(self._scatter_thresholds)
        for city, leaving_providers in leaving_providers.items():
            num_leaving_providers = len(leaving_providers)
            if num_leaving_providers < min_leaving_providers:
                continue

            self._valid_origin_cities_volume[city] = num_leaving_providers
            self._destination_cities.update(destination_cities[city])

    def _city_condition(self, city: City) -> list:
        if city in self._valid_origin_cities_volume:
            leaving_providers = self._valid_origin_cities_volume[city]
            data = self._scatter_thresholds[leaving_providers]
            city_scatter = CityScatter(
                **data,
                coord=city.city_coord,
                city_name=city.city_name
            )
            if city in self._destination_cities:
                city_scatter.map_attributes.edgecolor = 'red'

            return [city_scatter, TextBox(city_name=city.city_name,
                                          font="Roboto",
                                          fontsize=9,
                                          fontweight='normal',
                                          fontcolor="black",
                                          zorder=2)]

        elif city in self._destination_cities:
            city_scatter = CityScatter(
                radius=150,
                coord=city.city_coord,
                facecolor="gray",
                edgecolor="gray",
                marker="o",
                label=None,
                city_name=city.city_name
            )
            return [city_scatter, TextBox(city_name=city.city_name,
                                          font="Robot",
                                          fontsize=9,
                                          fontweight='normal',
                                          fontcolor="black",
                                          zorder=2)]

        return []

    def _assignment_condition(self, pa: ProviderAssignment) -> list:
        if pa.origin_city not in self._valid_origin_cities_volume:
            return []

        line_color = self._city_networks_handler.fetch_city_color(pa.origin_city)

        leaving_providers = self._valid_origin_cities_volume[pa.origin_city]
        if leaving_providers >= min(self._scatter_thresholds) and (pa.origin_city, pa.visiting_city) not in self._line_assignments_created:
            self._line_assignments_created.add((pa.origin_city, pa.visiting_city))
            return [
                Line(
                    linewidth=1000,
                    facecolor=line_color,
                    linestyle="-",
                    zorder=1,
                    origin_coordinate=pa.origin_city.city_coord,
                    visiting_coordinate=pa.visiting_city.city_coord
                )
            ]

        return []
