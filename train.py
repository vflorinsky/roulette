from random import randint, choice
from pathlib import Path
from bot import ThresholdBot
from gun import Gun
from copy import deepcopy


START_VOLUME = 8
N_ROTATIONS = 3
N_SLOTS = 6
MUTATION = {'use': True,
            'force': 15  # уровень шума в процентах от зашумляемого значения
            }


def fight(gun: Gun, players: list) -> str:
    while True:
        for p in players:
            p.action(gun=gun)
            if pistol.is_fired:
                return p.name


def mutation(x: float) -> float:
    return choice([-1, 1]) * 0.01 * MUTATION['force'] * x


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


def pair_generator(d: dict):
    iterator = iter(d.values())
    for item in iterator:
        yield item, next(iterator)


def selection(population: dict, pistol: Gun) -> dict:
    gen = pair_generator(population)
    new_population = dict()
    for pair in gen:
        winner = fight(gun=pistol,
                       players=[pair[0], pair[1]]
                       )
        new_population[winner] = deepcopy(population[winner])
    return new_population


def crossing(population: dict, n_rotations: int) -> dict:
    gen = pair_generator(population)
    new_population = deepcopy(population)
    for pair in gen:
        name = f"{pair[0].name}+{pair[1].name}"
        thrsh = 0.5 * (pair[0].threshold() + pair[1].threshold())
        if MUTATION['use']:
            thrsh = mutation(thrsh)
        new_population[name] = ThresholdBot(name=name,
                                            n_rotations=n_rotations,
                                            threshold=thrsh)
        # Устанавливаем максивальное число слотов как у первого родителя
        # через сеттер, потому что в конструкторе оно None.
        new_population[name].max_slots(value=pair[0].max_slots())
        # Установка нового значения порога происходит через сеттер,
        # чтобы избежать выхода порога за допустимый диапазон.
        new_population[name].threshold(value=thrsh)
    return new_population


if __name__ == "__main__":
    pistol = Gun(n_slots=N_SLOTS)

    # Начальная популяция
    population = init_population(n_individuals=START_VOLUME,
                                 n_rotations=N_ROTATIONS,
                                 threshold_interval=(0, pistol.n_slots))

    # Отбор
    population = selection(population=population, pistol=pistol)
    print(population)

    # Скрещивание
    population = crossing(population=population, n_rotations=N_ROTATIONS)
    print(population)
