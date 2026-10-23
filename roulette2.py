from core import RouletteCore
from gun import Gun
from player import Player
from bot import RandomBot, ThresholdBot, ProbabilityBot
from random import randint


N_ROTATIONS = 3
N_SLOTS = 6
BOTS = {'Шмардунг': RandomBot(name='Шмардунг',
                              n_rotations=N_ROTATIONS,
                              verbose=True),
        'Васян': ThresholdBot(name='Васян',
                              n_rotations=N_ROTATIONS,
                              threshold=0,
                              verbose=True),
        'Рандомалия Игруновна': ProbabilityBot(name='Рандомалия Игруновна',
                                               n_rotations=N_ROTATIONS,
                                               verbose=True,
                                               n_slots=N_SLOTS,
                                               probs=[0.4185478268921187, 0.7455516744430214, 0.8408586542202624, 0.3532215232690814, 0.6103112019611341, 0.3511231271935957, 0.3409706152630562, 0.44914211368300017, 0.4313287392108611, 0.5082800733584025, 0.2429346159344374, 0.32672971257072614, 0.5146509978127706, 0.6989829255010938, 0.7920422344951276, 0.3970790824245649, 0.34081339452669723, 0.833061797180818, 0.33890478675192376, 0.4131365923557873, 0.395970812938607, 0.3819871633359201, 0.5903554213507699, 0.710343360293204, 0.6254775984794106, 0.3839006770120489, 0.25104291472343504, 0.6801866710257445, 0.4738272240228625, 0.5010675708527752, 0.4391742257088504, 0.3301954118949278, 0.5201427616860754, 0.4665467328084169, 0.18066660350595076, 0.6339815299607019, 0.46683947717937657, 0.30393091170036735, 0.5286746807755188, 0.3541038935349009, 0.4986136540667118])
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

