import pandas as pd

from . import origin_group


class OriginGroupsHandler:

    def __init__(self):
        self.origin_groups = {}
        self.dual_origin_outpatient = []

    def group_origins(self, df: pd.DataFrame, city_coords: dict):
        df.apply(self._group_by_origin, city_coords=city_coords, axis=1)
        return self.origin_groups

    def _group_by_origin(self, row, city_coords: dict):
        origin = row['point_of_origin']
        destination = row['community']
        if origin not in self.origin_groups:
            self.origin_groups[origin] = origin_group.OriginGroup(origin=origin, origin_coord=city_coords[origin])

        self.origin_groups[origin].add_destination(destination)

    def determine_dual_origin_outpatient(self):
        if len(self.origin_groups):
            raise ValueError(f"{__name__} called when origin_groups is empty.")

        for origin_group_ in self.origin_groups.values():
            for outpatient in origin_group_.outpatients:
                if outpatient in origin_group_.keys():
                    self.dual_origin_outpatient.append(outpatient)
        return self.dual_origin_outpatient


