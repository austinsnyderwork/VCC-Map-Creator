import logging
from typing import Callable


class ThingContainer:

    def __init__(self, type_held, generate_key_func: Callable):
        self.type_held = type_held
        self.generate_key_func = generate_key_func
        self.things = {}

    def add_thing(self, thing):
        logging.debug(f"\tAdding thing to {self.type_held} container.")
        key = self.generate_key_func(type(thing), **thing.__dict__)
        self.things[key] = thing

    def get_thing(self, thing_type, **kwargs):
        key = self.generate_key_func(entity_type=thing_type,
                                     **kwargs)
        return self.things[key]

    def get_all_things(self):
        return list(self.things.values())