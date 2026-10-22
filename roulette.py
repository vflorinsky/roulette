from core import RouletteCore
from gun import Gun
from player import Player
from bot import RandomBot
from time import sleep
from random import randint


N_ROTATIONS = 3
N_SLOTS = 6
BOT_NAME = 'Электрический Мозг'


def set_options(n_rotations: int, bot_name: str = BOT_NAME):
    print("Добро пожаловать в Смертельную Рулетку, смельчак!")
    print(f"Как Вас зовут?")
    player_name = input()
    player_1 = Player(name=player_name, n_rotations=n_rotations)

    flag, x = True, 0
    while flag:
        print(f"С кем желаете сразиться, уважаемый(ая) {player_name}?")
        try:
            x = int(input("1 - с другим игроком\n"
                          "2 - c ИИ\n"))
        except ValueError:
            print("Не понимаю...")
        if x in [1, 2]:
            flag = False
    print("\n")
    if x == 1:
        print(f"Как зовут соперника?")
        player_name = input()
        player_2 = Player(name=player_name, n_rotations=n_rotations)
    else:
        print(f"Вашим соперником будет {bot_name}.")
        player_2 = RandomBot(name=bot_name, n_rotations=n_rotations, verbose=True)
    print("\n")
    flag, x, var = True, 0, ['орёл', 'решка']
    while flag:
        print("Теперь определимся, кто стреляет первым.\n"
              "Орёл или решка?")
        try:
            x = int(input(f"1 - {var[0]}\n"
                          f"2 - {var[1]}\n"))
        except ValueError:
            print("Не понимаю...")
        if x in [1, 2]:
            x -= 1
            flag = False
    print(f"Итак, Ваш выбор - {var[x]}")
    del var[x]
    print(f"Бросаю монету!")
    m = randint(0, 1)
    sleep(1)
    print("Ииии...")
    sleep(2)
    print("Еще летит")
    sleep(1)
    print("Упала и покатилась")
    sleep(2)
    print("Сейчас поймаю!")
    sleep(2)
    print("Ииии...")
    sleep(3)
    print("Барабанная дробь")
    sleep(3)
    if x == m:
        print("ТАДАААМ!")
        print("Первый выстрел - Ваш. Поздравляю!\n")
        return [player_1, player_2]
    else:
        if x == 0:
            xx = ""
        else:
            xx = "а"
        print(f"А выпал{xx} {var[0]}! Что ж, бывает. \n"
              f"Ваш выстрел - второй.")
        return [player_2, player_1]


if __name__ == "__main__":
    pistol = Gun(n_slots=N_SLOTS)

    players = set_options(n_rotations=N_ROTATIONS)
    # players = [RandomBot(name='Кузьбар', n_rotations=3, verbose=True),
    #            RandomBot(name='Шмартунг', n_rotations=3, verbose=True)]

    print("Приступим!\n")
    game = RouletteCore(gun=pistol, players=players, n_fights=1)
    result = game.fight()

    print('-' * 50)
    for name, res in result.items():
        if res == 1:
            print(f"{name} выжил в упорной схватке!")
        else:
            print(f"{name} успешно застрелился.")

    print("Дуэль окончена.")

