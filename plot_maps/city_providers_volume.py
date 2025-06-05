
from visual_elements.element_classes import CityScatter, ScatterAttributes, Line, LineAttributes, TextBox

from entities.entity_classes import City, ProviderAssignment
from entities.factory import EntitiesContainer
from environment_management.city_origin_networks import CityNetworksHandler
from plot_maps.base_classes import ConditionsController, ConditionsMap


class CityProviderVolumeConditionsController(ConditionsController):

    def __init__(self,
                 entities_container: EntitiesContainer,
                 city_networks_handler: CityNetworksHandler,
                 default_line_width: float,
                 ):
        self._city_networks_handler = city_networks_handler
        self._line_width = default_line_width

        self._leaving_providers = dict()
        self._visiting_providers = dict()

        self._setup(entities_container=entities_container)

        cmap = ConditionsMap()
        cmap.add_condition(condition=self._city_condition,
                           entity_type=City)
        cmap.add_condition(condition=self._assignment_condition,
                           entity_type=ProviderAssignment)
        cmap.add_condition(condition=self._text_box_condition,
                           entity_type=TextBox)

        super().__init__(conditions_map=cmap)

    def _setup(self, entities_container: EntitiesContainer):
        for pa in entities_container.provider_assignments:
            if pa.origin_city not in self._leaving_providers:
                self._leaving_providers[pa.origin_city] = 0
            self._leaving_providers[pa.origin_city] += 1

            if pa.visiting_city not in self._visiting_providers:
                self._visiting_providers[pa.visiting_city] = 0
            self._visiting_providers[pa.visiting_city] += 1

    def _city_condition(self, city: City) -> CityScatter | None:
        leaving_providers = self._leaving_providers[city]

        city_color = self._city_networks_handler.fetch_city_color(city)

        if leaving_providers in range(5, 11):
            return CityScatter(
                centroid=city.city_coord,
                radius=12,
                map_attributes={
                    ScatterAttributes.COLOR: city_color,
                    ScatterAttributes.MARKER: 'o'
                },
                city_name=city.city_name
            )
        elif leaving_providers in range(11, 16):
            return CityScatter(
                centroid=city.city_coord,
                radius=25,
                map_attributes={
                    ScatterAttributes.COLOR: city_color,
                    ScatterAttributes.MARKER: 'o'
                },
                city_name=city.city_name
            )
        elif leaving_providers in range(16, 21):
            return CityScatter(
                centroid=city.city_coord,
                radius=37,
                map_attributes={
                    ScatterAttributes.COLOR: city_color,
                    ScatterAttributes.MARKER: 'o'
                },
                city_name=city.city_name
            )
        elif leaving_providers >= 21:
            return CityScatter(
                centroid=city.city_coord,
                radius=50,
                map_attributes={
                    ScatterAttributes.COLOR: city_color,
                    ScatterAttributes.MARKER: 'o'
                },
                city_name=city.city_name
            )

        return None

    def _assignment_condition(self, pa: ProviderAssignment):
        origin_leaving_providers = self._leaving_providers[pa.origin_city]
        if origin_leaving_providers >= 5:
            line_color = self._city_networks_handler.fetch_city_color(pa.origin_city)

            return Line(
                origin_coordinate=pa.origin_city.city_coord,
                visiting_coordinate=pa.visiting_city.city_coord,
                width=self._line_width,
                map_attributes={
                    LineAttributes.COLOR: line_color
                }
            )

    def _text_box_condition(self, city: City):
        return TextBox(city_name=city.city_name)

