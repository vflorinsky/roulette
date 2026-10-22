from random import randint, choice, sample
from pathlib import Path
from bot import ThresholdBot, ShotIsImpossible
from gun import Gun
from copy import deepcopy


N_GENERATIONS = 50
START_VOLUME = 512
N_ROTATIONS = 3
N_SLOTS = 6
N_FIGHTS = 10000
MUTATION = {'use': False,
            'force': 15  # уровень шума в процентах от зашумляемого значения
            }


def fight(gun: Gun, players: list) -> dict:
    result = dict()
    players_ = deepcopy(players)
    for p in players_:
        result[p.name] = 0
    for i in range(N_FIGHTS):
        winner = None
        while winner is None:
            for p in players_:
                try:
                    p.action(gun=gun)
                    if pistol.is_fired:
                        for q in players_:
                            if q.name != p.name:
                                winner = q.name
                                break
                        break
                except ShotIsImpossible:  # p не смог выстрелить - все слоты заблокированы
                    winner = p.name
                    break
        result[winner] += 1
        for player in players_:
            player.reset()
        pistol.reset()
        if i == N_FIGHTS // 2:
            players_ = [players_[1], players_[0]]
    for k in result.keys():
        result[k] = result[k] / N_FIGHTS
    return result


def mutation(x: float) -> float:
    return choice([-1, 1]) * 0.01 * MUTATION['force'] * x


def init_population(n_individuals: int,
                    n_rotations: int,
                    threshold_interval: tuple,
                    max_slots: int) -> dict:
    """{имя_бота: бот}"""
    population = {}
    for i in range(n_individuals):
        name = f"0.{i}"  # "номер_поколения.номер_бота"
        population[name] = ThresholdBot(name=name,
                                        n_rotations=n_rotations,
                                        threshold=randint(threshold_interval[0],
                                                          threshold_interval[1]))
        population[name].max_slots(value=max_slots)
    return population


def pair_generator(d: dict):
    iterator = iter(d.values())
    for item in iterator:
        yield item, next(iterator)


def selection(population: dict, pistol: Gun) -> dict:
    gen = pair_generator(population)
    new_population = dict()
    for pair in gen:
        result = fight(gun=pistol,
                       players=[deepcopy(pair[0]), deepcopy(pair[1])]
                       )
        max_probability, winner = 0, None
        for k, v in result.items():
            if v > max_probability:
                max_probability = v
                winner = k
        new_population[winner] = deepcopy(population[winner])
        new_population[winner].reset()
    return new_population


def crossing(population: dict, n_rotations: int, generation: int) -> dict:
    gen = pair_generator(population)
    new_population = dict()
    bid = 0
    for pair in gen:
        # name = f"{pair[0].name}+{pair[1].name}"
        name = f"{generation}.{bid}"
        bid += 1
        # Значение __threshold у потомка
        thrsh = 0.5 * (pair[0].threshold() + pair[1].threshold())
        # Если нужно - потомок мутирует
        if MUTATION['use']:
            thrsh = mutation(thrsh)
        # Инициализируем потомка
        new_population[name] = ThresholdBot(name=name,
                                            n_rotations=n_rotations,
                                            threshold=thrsh)
        # Устанавливаем максивальное число слотов как у первого родителя
        # через сеттер, потому что в конструкторе оно None.
        new_population[name].max_slots(value=pair[0].max_slots())
        # Установка нового значения порога происходит через сеттер,
        # чтобы избежать выхода порога за допустимый диапазон.
        new_population[name].threshold(value=thrsh)
    # В новое поколение добавляем половину предков.
    # Нужно для сохранения разнообразия и чтобы размер каждого поколения
    # был степенью двойки.
    for p in sample(list(population.values()), len(new_population)):
        new_population[p.name] = p
    return new_population


if __name__ == "__main__":
    pistol = Gun(n_slots=N_SLOTS)

    # Начальная популяция
    population = init_population(n_individuals=START_VOLUME,
                                 n_rotations=N_ROTATIONS,
                                 threshold_interval=(0, pistol.n_slots),
                                 max_slots=pistol.n_slots)

    for generation in range(N_GENERATIONS):
        print(generation, len(population))
        trsh = [v.threshold() for _, v in population.items()]
        print(min(trsh), sum(trsh) / len(trsh), max(trsh), trsh)
        # Скрещивание, мутация
        population = crossing(population=population,
                              n_rotations=N_ROTATIONS,
                              generation=generation + 1)
        print("crossing", len(population))

        # Отбор
        population = selection(population=population, pistol=pistol)
        print("selection", len(population))
        print('-' * 50)

        if len(population) < 2:
            break

    print('-' * 50)
    for k, v in population.items():
        print(k)
        print(v.threshold())
