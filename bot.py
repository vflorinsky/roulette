from random import choice, random


class ShotIsImpossible(Exception):
    pass

# ===========================================================================================


class Bot:
    """Базовый класс"""

    def __init__(self, name: str, n_rotations: int, verbose: bool = False):
        self.__name = name
        self._n_rotations = n_rotations
        self._n_rotations_backup = n_rotations
        self._blocked_slots = []
        self._max_slots = None
        self._verbose = verbose

    def action(self, gun):
        if self._verbose:
            print(f"Ходит {self.__name}")
        if self._max_slots is None:
            self._max_slots = gun.n_slots
        try:
            if self._n_rotations > 0:
                flag = True
                while flag:
                    act = self._select_action(gun)
                    if act == 1:  # выстрелить
                        self._shot(gun)
                        if self._verbose:
                            print(f"{self.name} что-то сделал...\n")
                        return gun
                    elif act == 2:  # вращать
                        flag = self._rotate(gun)
                self._shot(gun)
            else:
                self._shot(gun)
        except ShotIsImpossible:
            if self._verbose:
                print(f"{self.name} перебрал все слоты и остался жив!\n")
            raise ShotIsImpossible
        if self._verbose:
            print(f"{self.name} что-то сделал...\n")
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

# ===========================================================================================


class RandomBot(Bot):
    """
    Решение вращать или стрелять принимается случайно.
    Если вращения закончились - только стреляет.
    """

    def _select_action(self, gun) -> int:
        if self._n_rotations > 0:
            return choice([1, 2])
        else:
            return 1

# ===========================================================================================


class ThresholdBot(Bot):
    """
    Если число заблокированных слотов не меньше заданного порога - вращает;
    иначе - стреляет.
    """

    def __init__(self, name: str,
                 n_rotations: int,
                 threshold: float,
                 verbose: bool = False):
        super().__init__(name=name, n_rotations=n_rotations, verbose=verbose)
        self.__threshold = threshold
        self.__verbose = verbose

    def _select_action(self, gun) -> int:
        if len(self._blocked_slots) >= self.__threshold and self._n_rotations > 0:
            return 2  # вращать
        else:
            return 1  # стрелять

    def cross_with(self, individual, spring_name):
        spring_threshold = 0.5 * (self.__threshold + individual.accessor())
        return ThresholdBot(name=spring_name,
                            n_rotations=self.n_rotations,
                            threshold=spring_threshold,
                            verbose=self.__verbose)

    def accessor(self, value: float = None) -> float or None:
        if value is not None:
            if value < 0:
                x = 0
            elif value > self._max_slots:
                x = self._max_slots
            else:
                x = value
            self.__threshold = x
        return self.__threshold

# ===========================================================================================


class ProbabilityBot(Bot):
    """
    Оценивает число раундов и для каждого устанавливает вероятность вращения.
    """

    def __init__(self, name: str,
                 n_rotations: int,
                 n_slots: int,
                 probs: list = None,
                 verbose: bool = False):
        super().__init__(name=name, n_rotations=n_rotations, verbose=verbose)
        self.__current_round = -1  # счетчик раундов включается после первого вызова _select_action
        if probs is None:
            self.__length = 2 * (n_slots - 1) * (n_rotations + 1) + 1
            self.__rotation_probs = [random() for _ in range(self.__length)]
            self.accessor()
        else:
            self.__length = len(probs)
            self.__rotation_probs = probs
            self.accessor(value=probs)

    def _select_action(self, gun) -> int:
        self.__current_round += 1
        if self._n_rotations > 0:
            if self.__rotation_probs[self.__current_round] >= 0.5:
                return 2  # вращать
            else:
                return 1  # стрелять
        else:
            return 1

    def accessor(self, value: list = None) -> list or None:
        if value is not None and len(value) == self.__length:
            self.__rotation_probs = value
        return self.__rotation_probs

    def reset(self):
        super().reset()
        self.__current_round = 0






