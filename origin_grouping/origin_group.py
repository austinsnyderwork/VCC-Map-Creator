import logging

import entities


class OriginGroup:

    def __init__(self, origin: entities.City, color: str):
        self.origin = origin
        self.color = color

        self.outpatients = set()
        self.outpatient_coords = {}

    def add_outpatient(self, outpatient: str):
        if outpatient == self.origin:
            logging.error(f"Attempted to add {outpatient} to {self.origin} group")
            return
        self.outpatients.add(outpatient)
