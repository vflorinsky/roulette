from player import Player
from gun import Gun


if __name__ == "__main__":

    pistol = Gun(n_slots=6)
    players = [Player(name='Гроканат', n_rotations=3),
               Player(name='Чучундра', n_rotations=3)]

    winner = None

    while winner is None:
        for p in players:
            p.action(gun=pistol)
            if pistol.is_fired:
                winner = p.name
                print("Ба-бах!\n")
                break
            else:
                print("Щёлк... Осечка!\n")

    print(f"Поздравляю, {winner}! Вы застрелились...")
