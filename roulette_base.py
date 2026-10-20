from bot import RandomBot, CleverBot
from gun import Gun


N_ROTATIONS = 3
N_SLOTS = 6
BOT_NAME = 'Электрический Мозг'
N_FIGHTS = 10000


def game(gun: Gun, players: list) -> dict:
    dead, n_moves = None, 0
    while dead is None:
        n_moves += 1
        for p in players:
            p.action(gun=gun)
            if pistol.is_fired:
                dead = p.name
                break
    return {"dead": dead, "n_moves": n_moves}


if __name__ == "__main__":

    pistol = Gun(n_slots=N_SLOTS)

    players = [CleverBot(name='Сепулька', n_rotations=N_ROTATIONS),
               RandomBot(name=BOT_NAME, n_rotations=N_ROTATIONS)]

    total = {f"{players[0].name}_death": 0,
             f"{players[0].name}_moves": 0,
             f"{players[1].name}_death": 0,
             f"{players[1].name}_moves": 0
             }

    for i in range(N_FIGHTS):
        result = game(gun=pistol, players=players)

        total[f"{result['dead']}_death"] += 1
        total[f"{result['dead']}_moves"] += result['n_moves']

        for p in players:
            p.reset()

    for k in total.keys():
        if k.split('_')[-1] == 'moves':
            total[k] = round(total[k] / N_FIGHTS, 2)
        else:
            total[k] = round(100 * total[k] / N_FIGHTS, 2)

    print(total)
