from random import randint
from copy import deepcopy


class Gun:

    def __init__(self, n_slots: int):
        self.__n_slots = n_slots
        self.__n_slots_default = n_slots
        self.__loaded_slot = 0
        self.rotate()
        self.__is_fired = False

    def rotate(self):
        self.__loaded_slot = randint(1, self.__n_slots)

    def shot(self, n: int):
        self.__is_fired = self.__loaded_slot == n

    def reset(self):
        self.__n_slots_default = deepcopy(self.__n_slots)
        self.__loaded_slot = 0
        self.rotate()
        self.__is_fired = False

    @property
    def is_fired(self):
        return self.__is_fired

    @property
    def n_slots(self):
        return self.__n_slots

