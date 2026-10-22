from pathlib import Path
from bot import RandomBot, ThresholdBot, ShotIsImpossible
from gun import Gun
from copy import deepcopy

SIMULATION = {'n_fights': 10000,
              'gun': {'n_slots': 6},
              'bots': {'ThresholdBot_1': {'threshold': 0, 'n_rotations': 3},
                       # 'ThresholdBot_2': {'threshold': 0, 'n_rotations': 3},
                       'RandomBot': {'n_rotations': 3},
                       }
              }
BOTS = {'RandomBot': RandomBot,
        'RandomBot_1': RandomBot,
        'RandomBot_2': RandomBot,
        'ThresholdBot': ThresholdBot,
        'ThresholdBot_1': ThresholdBot,
        'ThresholdBot_2': ThresholdBot,
        }


def del_from_players(players: list, names: list) -> list:
    if names is None or len(names) == 0:
        return players
    rv = []
    for p in players:
        if p.name not in names:
            rv.append(p)
    return rv


def game(gun: Gun, players: list) -> str:
    gun_, players_ = deepcopy(gun), [deepcopy(p) for p in players]
    loser, winner = None, None
    while loser is None:
        for p in players_:
            try:
                p.action(gun=gun_)
                if pistol.is_fired:
                    loser = p.name
                    break
            except ShotIsImpossible:  # p не смог выстрелить - все слоты заблокированы
                winner = p.name
                break
        players_ = del_from_players(players_, [loser, winner])
        if len(players_) == 1:
            loser = players_[0].name
    return loser


if __name__ == "__main__":

    # Инициализация
    pistol = Gun(n_slots=SIMULATION['gun']['n_slots'])
    players = [BOTS[bot_name](name=bot_name, **bot_opts) for bot_name, bot_opts in SIMULATION['bots'].items()]
    total = {}
    for player in players:
        total[player.name] = {'death_probability': 0,  # Вероятность застрелиться, %
                              }

    # Симуляция
    for i in range(SIMULATION['n_fights']):
        loser = game2(gun=pistol, players=players)

        total[loser]['death_probability'] += 1

        for player in players:
            player.reset()
        pistol.reset()

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

    # with open(f'sim_reports/simulation_{max_ind + 1}.txt', 'w') as f:
    #     f.write(f"OPTIONS = {SIMULATION.__str__()}\n")
    #     f.write(f"STATISTICS = {total.__str__()}\n")

    print(total)
