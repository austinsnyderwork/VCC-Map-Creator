import logging

import entities


class CityOriginNetwork:

    def __init__(self, origin: entities.City, color: str):
        self.origin = origin
        self.color = color

        self.outpatients = {}
        self.outpatient_coords = {}

    def add_outpatient(self, outpatient: VccClinicSite):
        if outpatient.name in self.outpatients:
            logging.info(f"Did not override Outpatient clinic '{outpatient.name}'")
            return
        self.outpatients[outpatient.name] = outpatient
