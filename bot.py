from random import choice


class ShotIsImpossible(Exception):
    pass


class Bot:
    """Базовый класс"""

    def __init__(self, name: str, n_rotations: int):
        self.__name = name
        self._n_rotations = n_rotations
        self._n_rotations_backup = n_rotations
        self._blocked_slots = []
        self._max_slots = None

    def action(self, gun):
        if self._max_slots is None:
            self._max_slots = gun.n_slots
        try:
            if self._n_rotations > 0:
                flag = True
                while flag:
                    act = self._select_action(gun)
                    if act == 1:  # выстрелить
                        self._shot(gun)
                        return gun
                    elif act == 2:  # вращать
                        flag = self._rotate(gun)
                self._shot(gun)
            else:
                self._shot(gun)
        except ShotIsImpossible:
            raise ShotIsImpossible
        return gun

    def _select_action(self, gun) -> int:
        pass

    def _shot(self, gun):
        ttt = list(set([i + 1 for i in range(self._max_slots)]).difference(set(self._blocked_slots)))
        if len(ttt) == 0:
            raise ShotIsImpossible
        s = choice(ttt)
        self._blocked_slots.append(s)
        gun.shot(s)

    def _rotate(self, gun) -> bool:
        if self._n_rotations > 1:
            gun.rotate()
            self._blocked_slots = []
            self._n_rotations -= 1
            return True
        else:
            self._n_rotations -= 1
            return False

    def max_slots(self, value: float = None) -> float or None:
        if value is not None:
            self._max_slots = value
        return self._max_slots

    def reset(self):
        self._n_rotations = self._n_rotations_backup
        self._blocked_slots = []

    @property
    def name(self):
        return self.__name

    @property
    def n_rotations(self):
        return self._n_rotations


class RandomBot(Bot):

    def _select_action(self, gun) -> int:
        if self._n_rotations > 0:
            return choice([1, 2])
        else:
            return 1


class ThresholdBot(Bot):

    def __init__(self, name: str, n_rotations: int, threshold: float):
        super().__init__(name=name, n_rotations=n_rotations)
        self.__threshold = threshold

    def _select_action(self, gun) -> int:
        if len(self._blocked_slots) >= self.__threshold and self._n_rotations > 0:
            return 2  # вращать
        else:
            return 1  # стрелять

    def threshold(self, value: float = None) -> float or None:
        if value is not None:
            if value < 0:
                x = 0
            elif value > self._max_slots:
                x = self._max_slots
            else:
                x = value
            self.__threshold = x
        return self.__threshold



