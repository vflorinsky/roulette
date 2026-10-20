from bot import RandomBot, CleverBot
from gun import Gun


N_ROTATIONS = 3
N_SLOTS = 6
BOT_NAME = 'Электрический Мозг'


def game(gun: Gun, players: list) -> dict:
    dead, winner, n_moves = None, None, 0
    while dead is None:
        n_moves += 1
        for p in players:
            p.action(gun=gun)
            if p.win:
                winner = p.name
                break
            if pistol.is_fired:
                dead = p.name
                break
    return {"dead": dead, "winner": winner, "n_moves": n_moves}


if __name__ == "__main__":

    pistol = Gun(n_slots=N_SLOTS)

    players = [CleverBot(name='Сепулька', n_rotations=N_ROTATIONS),
               RandomBot(name=BOT_NAME, n_rotations=N_ROTATIONS)]

    total = {f"{players[0].name}_death": 0,
             f"{players[0].name}_moves": 0,
             f"{players[0].name}_wins": 0,
             f"{players[1].name}_death": 0,
             f"{players[1].name}_moves": 0,
             f"{players[1].name}_wins": 0
             }

    for i in range(10):
        result = game(gun=pistol, players=players)

        total[f"{result['dead']}_death"] += 1
        total[f"{result['dead']}_moves"] += 1
        if result['winner'] is not None:
            total[f"{result['winner']}_wins"] += 1

        for p in players:
            p.reset()

        print(i, total)
