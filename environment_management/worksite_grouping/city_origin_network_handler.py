from .city_origin_network import CityOriginNetwork
import entities


class CityOriginNetworkHandler:

    def __init__(self, colors: list[str]):
        self.colors = colors
        self.city_origin_networks = {}
        self.dual_origin_outpatient = []

        self.colors_idx = 0

    def add_city_origin_network(self, city_origin_network: CityOriginNetwork, destination: entities.VccClinicSite):
        if city_origin_network.origin.city_name in self.city_origin_networks:
            raise RuntimeError(f"Attempted to add already existing origin city network with origin '{city_origin_network.origin}'."
                               f"Don't think this should be possible.")
        self.origin_groups[origin.city_name = origin_group]

    def add_site(self, clinic_site: entities.VccClinicSite)

    def apply_build_origin_networks(self, row, city_coords: dict, city_name_changes: dict):
        origin = row['point_of_origin']
        destination = row['community']

        if origin in city_name_changes:
            origin = city_name_changes[origin]

        if origin not in self.origin_groups:
            new_site = entities.VccClinicSite(name=origin,
                                     coord=city_coords[origin])
            self.origin_groups[origin] = OriginSiteGroup(origin=origin,
                                                                  color=self.colors[self.colors_idx],
                                                                  origin_coord=city_coords[origin])
            self.colors_idx += 1

        self.origin_groups[origin].add_outpatient(destination)

    def filter_origin_groups(self, filter_origins: list[str] = None, filter_outpatients: list[str] = None):
        new_origin_groups = {}
        for origin, origin_group in self.origin_groups.items():
            if filter_origins and origin not in filter_origins:
                continue
            if filter_outpatients:
                filtered_outpatients = set(outpatient for outpatient in origin_group.outpatients if outpatient in filter_outpatients)
                origin_group.outpatients = filtered_outpatients
            new_origin_groups[origin] = origin_group
        self.origin_groups = new_origin_groups

    def determine_dual_origin_outpatient(self):
        if len(self.origin_groups) == 0:
            raise ValueError(f"{__name__} called when origin_groups is empty.")

        for origin_group_ in self.origin_groups.values():
            for outpatient in origin_group_.outpatients:
                if outpatient in self.origin_groups.keys():
                    self.dual_origin_outpatient.append(outpatient)
        return self.dual_origin_outpatient


