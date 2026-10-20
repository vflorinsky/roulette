from pathlib import Path
from bot import RandomBot, ThresholdBot
from gun import Gun

SIMULATION = {'n_fights': 10000,
              'gun': {'n_slots': 6},
              'bots': {# 'ThresholdBot': {'threshold': 3, 'n_rotations': 3},
                       'ThresholdBot_1': {'threshold': 3, 'n_rotations': 3},
                       'ThresholdBot_2': {'threshold': 3, 'n_rotations': 3},
                       }
              }
BOTS = {'RandomBot': RandomBot,
        'RandomBot_1': RandomBot,
        'RandomBot_2': RandomBot,
        'ThresholdBot': ThresholdBot,
        'ThresholdBot_1': ThresholdBot,
        'ThresholdBot_2': ThresholdBot,
        }


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

    # Расчет статистики
    for k in total.keys():
        for kk in total[k].keys():
            total[k][kk] = round(total[k][kk] / SIMULATION['n_fights'], 2)

    # Сохраняем результат
    folder_path = Path("sim_reports")

    max_ind = 0
    for file_name in [f.name for f in folder_path.iterdir() if f.is_file()]:
        try:
            ind = int(file_name.split('.')[0].split('_')[1])
        except ValueError:
            continue
        max_ind = max(max_ind, ind)

    with open(f'sim_reports/simulation_{max_ind + 1}.txt', 'w') as f:
        f.write(f"OPTIONS = {SIMULATION.__str__()}\n")
        f.write(f"STATISTICS = {total.__str__()}\n")

    print(total)
