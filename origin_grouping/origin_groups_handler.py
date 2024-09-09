import pandas as pd

from . import origin_group


class OriginGroupsHandler:

    def __init__(self):
        self.origin_groups = {}
        self.dual_origin_outpatient = []

    def group_origins(self, row, city_coords: dict):
        origin = row['point_of_origin']
        destination = row['community']
        if origin not in self.origin_groups:
            self.origin_groups[origin] = origin_group.OriginGroup(origin=origin, origin_coord=city_coords[origin])

        self.origin_groups[origin].add_outpatient(destination)

    def determine_dual_origin_outpatient(self):
        if len(self.origin_groups):
            raise ValueError(f"{__name__} called when origin_groups is empty.")

        for origin_group_ in self.origin_groups.values():
            for outpatient in origin_group_.outpatients:
                if outpatient in origin_group_.keys():
                    self.dual_origin_outpatient.append(outpatient)
        return self.dual_origin_outpatient


