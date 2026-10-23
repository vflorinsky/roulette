from gun import Gun
from player import Player
from copy import deepcopy
from bot import Bot, ShotIsImpossible


class RouletteCore:

    def __init__(self, gun: Gun, players: list[Player or Bot], n_fights: int):
        self._gun = gun
        self._players = players
        self._n_fights = n_fights

    @staticmethod
    def _get_duel_winner(players: list,  # только два игрока
                         loser: str) -> str:
        for p in players:
            if p.name != loser:
                return p.name

    def _duel(self, players: list) -> str:
        players_ = [deepcopy(p) for p in players]
        winner = None
        while winner is None:
            for p in players_:
                try:
                    p.action(gun=self._gun)
                    if self._gun.is_fired:
                        winner = self._get_duel_winner(players=players_, loser=p.name)
                        break
                except ShotIsImpossible:  # p не смог выстрелить - все слоты заблокированы
                    winner = p.name
                    break
        return winner

    def fight(self) -> dict:
        """{имя_бота: вероятность_выигрыша}"""
        result = dict()
        players_ = deepcopy(self._players)
        for p in players_:
            result[p.name] = 0
        for i in range(self._n_fights):
            winner = self._duel(players=players_)
            result[winner] += 1
            if self._n_fights > 1:  # если одна дуэль, ресет не нужен
                for player in players_:
                    player.reset()
                self._gun.reset()
            if i == self._n_fights // 2:
                players_ = [players_[1], players_[0]]
        for k in result.keys():
            result[k] = result[k] / self._n_fights
        return result
