from . import origin_group


class OriginGroupsHandler:

    def __init__(self, colors: list[str]):
        self.colors = colors
        self.origin_groups = {}
        self.dual_origin_outpatient = []

        self.colors_idx = 0

    def group_origins(self, row, city_coords: dict, origins_to_group_together: dict):
        origin = row['point_of_origin']
        destination = row['community']

        if origin in origins_to_group_together:
            origin = origins_to_group_together[origin]

        if origin not in self.origin_groups:
            self.origin_groups[origin] = origin_group.OriginGroup(origin=origin,
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


