from player import Player
from bot import RandomBot
from gun import Gun
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
        player_2 = RandomBot(name=bot_name, n_rotations=n_rotations)
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
    sleep(0.5)
    print("Ииии...")
    sleep(1)
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
        print("Первый выстрел - Ваш. Поздравляю!")
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

    players = set_options(n_rotations=N_ROTATIONS)
    pistol = Gun(n_slots=N_SLOTS)
    print("Приступим!\n")

    winner = None

    while winner is None:
        for p in players:
            print(f"Ваш ход, {p.name}!")
            p.action(gun=pistol)
            if pistol.is_fired:
                winner = p.name
                print("Ба-бах!\n")
                break
            else:
                print("Щёлк... Осечка!")
            print('-' * 50 + '\n')

    print(f"Поздравляю, {winner}! Вы застрелились...")
