from random import choice, randint


class Bot:
    """Базовый класс"""

    def __init__(self, name: str, n_rotations: int):
        self.__name = name
        self._n_rotations = n_rotations
        self._n_rotations_backup = n_rotations
        self._blocked_slots = []

    def action(self, gun):
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
        return gun

    def _select_action(self, gun) -> int:
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

    def reset(self):
        self._n_rotations = self._n_rotations_backup
        self._blocked_slots = []

    @property
    def name(self):
        return self.__name


class RandomBot(Bot):

    def _select_action(self, gun) -> int:
        if self._n_rotations > 0:
            return choice([1, 2])
        else:
            return 1

    def _shot(self, gun):
        ttt = list(set([i + 1 for i in range(gun.n_slots)]).difference(set(self._blocked_slots)))
        s = choice(ttt)
        self._blocked_slots.append(s)
        gun.shot(s)


class CleverBot(Bot):

    def _select_action(self, gun) -> int:
        if len(self._blocked_slots) >= gun.n_slots // 2 and self._n_rotations > 0:
            return 2  # вращать
        else:
            return 1  # стрелять

    def _shot(self, gun):
        ttt = list(set([i + 1 for i in range(gun.n_slots)]).difference(set(self._blocked_slots)))
        s = choice(ttt)
        self._blocked_slots.append(s)
        gun.shot(s)


