from random import choice, randint


class RandomBot:

    def __init__(self, name: str, n_rotations: int):
        self.__name = name
        self.__n_rotations = n_rotations
        self.__blocked_slots = []

    def action(self, gun):
        if self.__n_rotations > 0:
            flag = True
            while flag:
                act = self.__select_action()
                if act == 1:  # выстрелить
                    self.__shot(gun)
                    return gun
                elif act == 2:  # вращать
                    flag = self.__rotate(gun)
            self.__shot(gun)
        else:
            self.__shot(gun)
        return gun

    @staticmethod
    def __select_action() -> int:
        return choice([1, 2])

    def __shot(self, gun):
        s = randint(1, gun.n_slots)
        while s in self.__blocked_slots:
            s = randint(1, gun.n_slots)
        self.__blocked_slots.append(s)
        gun.shot(s)

    def __rotate(self, gun) -> bool:
        if self.__n_rotations > 1:
            gun.rotate()
            self.__blocked_slots = []
            self.__n_rotations -= 1
            return True
        else:
            self.__n_rotations -= 1
            return False

    @property
    def name(self):
        return self.__name



