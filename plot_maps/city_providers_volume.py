
from entities.entity_classes import City, ProviderAssignment
from entities.factory import EntitiesContainer
from environment_management.city_origin_networks import CityNetworksHandler
from plot_maps.base_classes import ConditionsController, ConditionsMap
from visual_elements.element_classes import CityScatter, Line, TextBox


class CityProviderVolumeConditionsController(ConditionsController):

    def __init__(self,
                 entities_container: EntitiesContainer,
                 city_networks_handler: CityNetworksHandler
                 ):
        self._leaving_providers = dict()
        self._visiting_providers = dict()

        self._setup(entities_container=entities_container)

        cmap = ConditionsMap()
        cmap.add_condition(condition=self._city_condition,
                           entity_type=City)
        """cmap.add_condition(condition=self._assignment_condition,
                           entity_type=ProviderAssignment)"""

        super().__init__(conditions_map=cmap,
                         city_networks_handler=city_networks_handler)

    def _setup(self, entities_container: EntitiesContainer):
        print(f"Setting up {self.__class__.__name__} EntitiesContainer.")
        for pa in entities_container.provider_assignments:
            if pa.origin_city not in self._leaving_providers:
                self._leaving_providers[pa.origin_city] = 0
            self._leaving_providers[pa.origin_city] += 1

            if pa.visiting_city not in self._visiting_providers:
                self._visiting_providers[pa.visiting_city] = 0
            self._visiting_providers[pa.visiting_city] += 1

    def _city_condition(self, city: City) -> tuple[CityScatter, TextBox] | None:
        leaving_providers = self._leaving_providers[city] if city in self._leaving_providers else 0

        scatter = None
        text_box = None
        if leaving_providers in range(5, 11):
            scatter = CityScatter(
                coord=city.city_coord,
                radius=0.04,
                map_attributes={
                    "color": "red",
                    "marker": "o",
                    "label": "5-11"
                },
                city_name=city.city_name
            )
            text_box = TextBox(city_name=city.city_name)

        elif leaving_providers in range(11, 16):
            scatter = CityScatter(
                coord=city.city_coord,
                radius=0.04,
                map_attributes={
                    "color": 'blue',
                    "marker": "o",
                    "label": "11-16"
                },
                city_name=city.city_name
            )
            text_box = TextBox(city_name=city.city_name)

        elif leaving_providers in range(16, 21):
            scatter = CityScatter(
                coord=city.city_coord,
                radius=0.04,
                map_attributes={
                    "color": "orange",
                    "marker": "o",
                    "label": "16-21"
                },
                city_name=city.city_name
            )
            text_box = TextBox(city_name=city.city_name)

        elif leaving_providers >= 21:
            scatter = CityScatter(
                coord=city.city_coord,
                radius=0.04,
                map_attributes={
                    "color": "black",
                    "marker": "o",
                    "label": "21+"
                },
                city_name=city.city_name
            )
            text_box = TextBox(city_name=city.city_name)

        return scatter, text_box

    def _assignment_condition(self, pa: ProviderAssignment) -> tuple[Line, None] | tuple[None, None]:
        if pa.origin_city not in self._leaving_providers:
            return None, None

        line_color = self._city_networks_handler.fetch_city_color(pa.origin_city)

        origin_leaving_providers = self._leaving_providers[pa.origin_city]
        if origin_leaving_providers >= 5:
            return (
                Line(
                    origin_coordinate=pa.origin_city.city_coord,
                    visiting_coordinate=pa.visiting_city.city_coord,
                    map_attributes={
                        "color": line_color,
                        "linestyle": "-",
                        "linewidth": 0.1
                    }
                ),
                None
            )

        return None, None
