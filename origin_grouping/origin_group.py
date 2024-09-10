

class OriginGroup:

    def __init__(self, origin: str, origin_coord, color: str):
        self.origin = origin
        self.origin_coord = origin_coord
        self.color = color

        self.outpatients = set()
        self.outpatient_coords = {}

    def add_outpatient(self, outpatient: str):
        self.outpatients.add(outpatient)
