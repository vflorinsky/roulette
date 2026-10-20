from random import randint
from pathlib import Path
from bot import ThresholdBot
from gun import Gun
from copy import deepcopy


START_VOLUME = 8
N_ROTATIONS = 3


def fight(gun: Gun, players: list) -> str:
    while True:
        for p in players:
            p.action(gun=gun)
            if pistol.is_fired:
                return p.name


def init_population(n_individuals: int,
                    n_rotations: int,
                    threshold_interval: tuple) -> dict:
    """{имя_бота: бот}"""
    population = {}
    for i in range(n_individuals):
        name = f"0.{i}"  # "номер_поколения.номер_бота"
        population[name] = ThresholdBot(name=name,
                                        n_rotations=n_rotations,
                                        threshold=randint(threshold_interval[0],
                                                          threshold_interval[1]))
    return population


def selection(population: dict, pistol: Gun) -> dict:
    i, names = 0, list(population.keys())
    new_population = dict()
    while i < len(names):
        winner = fight(gun=pistol,
                       players=[population[names[i]],
                                population[names[i + 1]]
                                ]
                       )
        i += 2
        new_population[winner] = deepcopy(population[winner])
    return new_population


if __name__ == "__main__":
    pistol = Gun(n_slots=6)

    # Начальная популяция
    population = init_population(n_individuals=START_VOLUME,
                                 n_rotations=N_ROTATIONS,
                                 threshold_interval=(0, pistol.n_slots))
    # Отбор
    population = selection(population=population, pistol=pistol)
    print(population)
