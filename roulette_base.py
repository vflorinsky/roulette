from player import Player
from bot import RandomBot
from gun import Gun


N_ROTATIONS = 3
N_SLOTS = 6
BOT_NAME = 'Электрический Мозг'


if __name__ == "__main__":

    pistol = Gun(n_slots=N_SLOTS)

    players = [#Player(name='Зозондр', n_rotations=N_ROTATIONS),
               RandomBot(name=BOT_NAME, n_rotations=N_ROTATIONS)]

    # for _ in range(5):
    #     print(players[1]._select_action())

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
