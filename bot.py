from random import choice, randint


class Bot:
    """Базовый класс"""

    def __init__(self, name: str, n_rotations: int):
        self.__name = name
        self._n_rotations = n_rotations
        self._blocked_slots = []

    def action(self, gun):
        if self._n_rotations > 0:
            flag = True
            while flag:
                act = self._select_action()
                if act == 1:  # выстрелить
                    self._shot(gun)
                    return gun
                elif act == 2:  # вращать
                    flag = self._rotate(gun)
            self._shot(gun)
        else:
            self._shot(gun)
        return gun

    @staticmethod
    def _select_action() -> int:
        pass

    def _shot(self, gun):
        pass

    def _rotate(self, gun) -> bool:
        if self._n_rotations > 1:
            gun.rotate()
            self._blocked_slots = []
            self._n_rotations -= 1
            return True
        else:
            self._n_rotations -= 1
            return False

    @property
    def name(self):
        return self.__name


class RandomBot(Bot):

    @staticmethod
    def _select_action() -> int:
        return choice([1, 2])

    def _shot(self, gun):
        s = randint(1, gun.n_slots)
        while s in self._blocked_slots:
            s = randint(1, gun.n_slots)
        self._blocked_slots.append(s)
        gun.shot(s)


