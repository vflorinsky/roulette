from bot import RandomBot, ThresholdBot
from gun import Gun

SIMULATION = {'n_fights': 10000,
              'gun': {'n_slots': 6},
              'bots': {'ThresholdBot': {'threshold': 3, 'n_rotations': 3},
                       'RandomBot': {'n_rotations': 3}
                       }
              }
BOTS = {'RandomBot': RandomBot, 'ThresholdBot': ThresholdBot}


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

    # Инициализация
    pistol = Gun(n_slots=SIMULATION['gun']['n_slots'])
    players = [BOTS[bot_name](name=bot_name, **bot_opts) for bot_name, bot_opts in SIMULATION['bots'].items()]
    total = {}
    for player in players:
        total[player.name] = {'death_probability': 0,  # Вероятность застрелиться, %
                              'moves': 0  # Среднее число ходов
                              }

    # Симуляция
    for i in range(SIMULATION['n_fights']):
        result = game(gun=pistol, players=players)

        total[result['dead']]['death_probability'] += 1
        total[result['dead']]['moves'] += result['n_moves']

        for player in players:
            player.reset()

        # Во второй половине симуляции меняем порядок игроков, чтобы нивелировать эффект первого хода.
        if i == SIMULATION['n_fights'] // 2:
            players = [players[1], players[0]]

    # Вывод статистики
    for k in total.keys():
        for kk in total[k].keys():
            total[k][kk] = round(total[k][kk] / SIMULATION['n_fights'], 2)

    print(total)
