from typing import Callable


class ThingContainer:

    def __init__(self, generate_key_func: Callable):
        self.generate_key_func = generate_key_func
        self.things = {}

    def add_thing(self, thing, **kwargs):
        key = self.generate_key_func(type(thing), **kwargs)
        self.things[key] = thing

    def get_thing(self, thing_type, **kwargs):
        key = self.generate_key_func(entity_type=thing_type,
                                     **kwargs)
        return self.things[key]

    def get_all_things(self):
        return list(self.things.values())