

class OriginGroup:

    def __init__(self, origin: str):
        self.origin = origin

        self.outpatients = set()

    def add_outpatient(self, outpatient: str):
        self.outpatients.add(outpatient)
