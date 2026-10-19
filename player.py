class Player:

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

    def __select_action(self) -> int:
        x = 0
        print(f"Ваш ход, {self.__name}!")
        while x not in {1, 2}:
            try:
                x = int(input(f"1 - выстрелить;\n"
                              f"2 - вращать барабан\n"))
            except ValueError:
                print("Не понимаю...")
            if x not in {1, 2}:
                print("Вам надо ввести 1 либо 2:")
        print('\n')
        return x

    def __shot(self, gun):
        s = 0
        if len(self.__blocked_slots) > 0:
            message = (f"Слоты {', '.join(self.__blocked_slots)} заблокированы.\n"
                       f"В какой слот (от 1 до {gun.n_slots}) стреляем, {self.__name}?\n")
        else:
            message = f"В какой слот (от 1 до {gun.n_slots}) стреляем, {self.__name}?\n"
        while True:
            try:
                s = int(input(message))
            except ValueError:
                pass
            if str(s) in self.__blocked_slots:
                print("Вы не можете выбрать заблокированный слот!")
            elif 1 <= s <= gun.n_slots:
                break
        gun.shot(s)
        self.__blocked_slots.append(str(s))

    def __rotate(self, gun) -> bool:
        if self.__n_rotations > 1:
            gun.rotate()
            self.__blocked_slots = []
            self.__n_rotations -= 1
            print(f"Все слоты разблокированы.\n"
                  f"Экономьте вращения, {self.__name}: их осталось лишь {self.__n_rotations}.")
            return True
        else:
            self.__n_rotations -= 1
            print("Вращений больше нет - закончились. Теперь только стрелять!")
            return False

    @property
    def name(self):
        return self.__name
