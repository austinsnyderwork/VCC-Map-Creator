import logging

from entities.vcc_clinic_site import VccClinicSite


class CityOriginNetwork:

    def __init__(self, origin: VccClinicSite, color: str):
        self.origin = origin
        self.color = color

        self.outpatients = {}
        self.outpatient_coords = {}

    def add_outpatient(self, outpatient: VccClinicSite):
        if outpatient.name in self.outpatients:
            logging.info(f"Did not override Outpatient clinic '{outpatient.name}'")
            return
        self.outpatients[outpatient.name] = outpatient
