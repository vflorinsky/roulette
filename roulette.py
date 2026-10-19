from player import Player
from bot import RandomBot
from gun import Gun


if __name__ == "__main__":

    pistol = Gun(n_slots=6)
    players = [Player(name='Гроканат', n_rotations=3),
               RandomBot(name='Чучундра', n_rotations=3)]

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
