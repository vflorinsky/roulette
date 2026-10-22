from gun import Gun
from copy import deepcopy
from bot import ShotIsImpossible


class RouletteCore:

    def get_duel_winner(players: list,  # только два игрока
                        loser: str) -> str:
        for p in players:
            if p.name != loser:
                return p.name

    def duel(gun: Gun, players: list) -> str:
        gun_, players_ = deepcopy(gun), [deepcopy(p) for p in players]
        winner = None
        while winner is None:
            for p in players_:
                try:
                    p.action(gun=gun_)
                    if gun_.is_fired:
                        winner = get_duel_winner(players=players_, loser=p.name)
                        break
                except ShotIsImpossible:  # p не смог выстрелить - все слоты заблокированы
                    winner = p.name
                    break
        return winner

    def fight(gun: Gun, players: list, n_fights: int) -> dict:
        result = dict()
        gun_, players_ = deepcopy(gun), deepcopy(players)
        for p in players_:
            result[p.name] = 0
        for i in range(n_fights):
            winner = duel(gun=gun_, players=players_)
            result[winner] += 1
            for player in players_:
                player.reset()
            pistol.reset()
            if i == n_fights // 2:
                players_ = [players_[1], players_[0]]
        for k in result.keys():
            result[k] = result[k] / n_fights
        return result
