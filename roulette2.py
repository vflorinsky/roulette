from core import RouletteCore
from gun import Gun
from player import Player
from bot import RandomBot, ThresholdBot, ProbabilityBot
from time import sleep
from random import randint


N_ROTATIONS = 3
N_SLOTS = 6
BOTS = {'Шмардунг': RandomBot(name='Шмардунг',
                              n_rotations=N_ROTATIONS,
                              verbose=True),
        'Васян': ThresholdBot(name='Васян',
                              n_rotations=N_ROTATIONS,
                              threshold=3,
                              verbose=True),
        'Рандомалия Игруновна': ProbabilityBot(name='Рандомалия Игруновна',
                                               n_rotations=N_ROTATIONS,
                                               verbose=True,
                                               n_slots=N_SLOTS,
                                               probs=[0.4178687111973717, 0.013624500473614859, 1, 0.5220252893473505, 0.41890325551401386, 0.4171216742168011, 0.9101932150881249, 0.8787717998419473, 0.07867651903534859, 0.2702861431254712, 0.08568612501846179, 0.3885546116369757, 0.9144354705059612, 0.10890457330871745, 0.11180504461988214, 0.14325939008942615, 0.6689663371913013])
        }


def set_options(n_rotations: int):
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
        competitors, i, select_message = {}, 1, ""
        for k in BOTS.keys():
            competitors[i] = k
            select_message += f"{i} - {k}\n"
            i += 1
        flag = True
        while flag:
            print(f"Выберите соперника:")
            try:
                x = int(input(select_message))
            except ValueError:
                print("Не понимаю...")
            if x in competitors.keys():
                flag = False
        player_2 = BOTS[competitors[x]]
        print(f"Ваш соперник - {player_2.name}")
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
    if x == m:
        print("ТАДАААМ!")
        print("Первый выстрел - Ваш. Поздравляю!\n")
        return [player_1, player_2]
    else:
        print(f"А монета говорит - {var[0]}! Что ж, бывает. \n"
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

