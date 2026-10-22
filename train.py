import logging
from logging.handlers import RotatingFileHandler
from random import randint, choice, sample
from pathlib import Path
from bot import ThresholdBot, ShotIsImpossible
from gun import Gun
from copy import deepcopy
from statistics import median


TRAIN_SETTINGS = {'n_generations': 50,
                  'start_volume': 4,
                  'n_fights': 10000,
                  'mutation': {'use': False,
                               'force': 15  # уровень шума в процентах от зашумляемого значения
                               },
                  'gun': {'n_slots': 6},
                  'bot': {'n_rotations': 3,
                          'threshold_interval': (3, 6)}
                  }

LOG_SETTINGS = {'path': Path('logs') / 'train',
                'name': 'ThresholdBot',
                'format': '%(asctime)s - %(name)s - %(message)s',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 3}


def del_from_players(players: list, names: list) -> list:
    if names is None or len(names) == 0:
        return players
    rv = []
    for p in players:
        if p.name not in names:
            rv.append(p)
    return rv


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
                if p.is_alive:
                    winner = get_duel_winner(players=players_, loser=p.name)
                    break
            except ShotIsImpossible:  # p не смог выстрелить - все слоты заблокированы
                winner = p.name
                break
    return winner


def fight(gun: Gun, players: list) -> dict:
    result = dict()
    gun_, players_ = deepcopy(gun), deepcopy(players)
    for p in players_:
        result[p.name] = 0
    for i in range(TRAIN_SETTINGS['n_fights']):
        winner = duel(gun=gun_, players=players_)
        result[winner] += 1
        for player in players_:
            player.reset()
        pistol.reset()
        if i == TRAIN_SETTINGS['n_fights'] // 2:
            players_ = [players_[1], players_[0]]
    for k in result.keys():
        result[k] = result[k] / TRAIN_SETTINGS['n_fights']
    return result


def mutation(x: float) -> float:
    return choice([-1, 1]) * 0.01 * TRAIN_SETTINGS['mutation']['force'] * x


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
        # thrsh = 0.5 * (pair[0].threshold() + pair[1].threshold())
        thrsh = max(pair[0].threshold(), pair[1].threshold())
        # Если нужно - потомок мутирует
        if TRAIN_SETTINGS['mutation']['use']:
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
    for name in new_population.keys():
        new_population[name].reset()
    return new_population


if __name__ == "__main__":

    logger = logging.getLogger(LOG_SETTINGS['name'])
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(LOG_SETTINGS['format'])
    file_handler = RotatingFileHandler(
        filename=f"{LOG_SETTINGS['path'] / LOG_SETTINGS['name']}.log",
        maxBytes=LOG_SETTINGS['maxBytes'],
        backupCount=LOG_SETTINGS['backupCount'],
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("START")
    logger.info(f"TRAIN_SETTINGS = {TRAIN_SETTINGS.__str__()}")

    pistol = Gun(n_slots=TRAIN_SETTINGS['gun']['n_slots'])

    # Начальная популяция
    population = init_population(n_individuals=TRAIN_SETTINGS['start_volume'],
                                 n_rotations=TRAIN_SETTINGS['bot']['n_rotations'],
                                 threshold_interval=TRAIN_SETTINGS['bot']['threshold_interval'],
                                 max_slots=pistol.n_slots)

    for generation in range(TRAIN_SETTINGS['n_generations']):
        logger.info(f"generation = {generation}")
        logger.info(f"volume = {len(population)}")

        trsh = [v.threshold() for _, v in population.items()]

        logger.info(f"trsh mean = {sum(trsh) / len(trsh)}")
        logger.info(f"trsh median = {median(trsh)}")

        # Скрещивание, мутация
        population = crossing(population=population,
                              n_rotations=TRAIN_SETTINGS['bot']['n_rotations'],
                              generation=generation + 1)
        logger.info(f"volume after crossing = {len(population)}")

        # Отбор
        population = selection(population=population, pistol=pistol)
        logger.info(f"volume after selection = {len(population)}")
        logger.info('-' * 50)

        if len(population) < 2:
            break

    logger.info(f"survive = {len(population)}")
    for v in population.values():
        bot = v
    logger.info(f"winner = {bot.__dict__.__str__()}")
    logger.info("END")
