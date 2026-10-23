import logging
from logging.handlers import RotatingFileHandler
from random import randint, choice, sample
from pathlib import Path
from bot import ProbabilityBot
from gun import Gun
from copy import deepcopy
from statistics import median
from core import RouletteCore


TRAIN_SETTINGS = {'n_generations': 50,
                  'start_volume': 4,
                  'n_fights': 10000,
                  'mutation': {'use': False,
                               'force': 15  # уровень шума в процентах от зашумляемого значения
                               },
                  'gun': {'n_slots': 6},
                  'bot': {'n_rotations': 3,
                          'n_slots': 6}
                  }

LOG_SETTINGS = {'path': Path('logs') / 'train',
                'name': 'ProbabilityBot',
                'format': '%(asctime)s - %(name)s - %(message)s',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 3}


def mutation(x: float) -> float:
    return choice([-1, 1]) * 0.01 * TRAIN_SETTINGS['mutation']['force'] * x


def init_population(n_individuals: int,
                    n_rotations: int,
                    max_slots: int) -> dict:
    """{имя_бота: бот}"""
    population = {}
    for i in range(n_individuals):
        name = f"0.{i}"  # "номер_поколения.номер_бота"
        population[name] = ProbabilityBot(name=name,
                                          n_rotations=n_rotations,
                                          n_slots=max_slots)
    return population


def pair_generator(d: dict):
    iterator = iter(d.values())
    for item in iterator:
        yield item, next(iterator)


def selection(population: dict, pistol: Gun) -> dict:
    gen = pair_generator(population)
    new_population = dict()
    for pair in gen:
        sim = RouletteCore(gun=pistol,
                           players=[deepcopy(pair[0]), deepcopy(pair[1])],
                           n_fights=TRAIN_SETTINGS['n_fights'])
        result = sim.fight()
        max_probability, winner = 0, None
        for k, v in result.items():
            if v > max_probability:
                max_probability = v
                winner = k
        new_population[winner] = deepcopy(population[winner])
        new_population[winner].reset()
    return new_population


def crossing(population: dict,
             n_rotations: int,
             generation: int,
             n_slots: int) -> dict:
    gen = pair_generator(population)
    new_population = dict()
    bid = 0
    for pair in gen:
        # name = f"{pair[0].name}+{pair[1].name}"
        name = f"{generation}.{bid}"
        bid += 1
        # Значение __rotation_probs у потомка
        spring_probs = []
        for a, b in zip(pair[0].probabilites(), pair[1].probabilites()):
            spring_probs.append(0.5 * (a + b))
        # Если нужно - потомок мутирует
        if TRAIN_SETTINGS['mutation']['use']:
            thrsh = mutation(thrsh)
        # Инициализируем потомка
        new_population[name] = ProbabilityBot(name=name,
                                              n_rotations=n_rotations,
                                              n_slots=n_slots)
        new_population[name].probabilites(value=spring_probs)
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
                                 max_slots=pistol.n_slots)

    for generation in range(TRAIN_SETTINGS['n_generations']):
        logger.info(f"generation = {generation}")
        logger.info(f"volume = {len(population)}")

        # trsh = [v.threshold() for _, v in population.items()]
        #
        # logger.info(f"trsh mean = {sum(trsh) / len(trsh)}")
        # logger.info(f"trsh median = {median(trsh)}")

        # Скрещивание, мутация
        population = crossing(population=population,
                              n_rotations=TRAIN_SETTINGS['bot']['n_rotations'],
                              generation=generation + 1,
                              n_slots=TRAIN_SETTINGS['bot']['n_rotations'])
        logger.info(f"volume after crossing = {len(population)}")

        # Отбор
        population = selection(population=population, pistol=pistol)
        # logger.info(f"volume after selection = {len(population)}")
        # logger.info('-' * 50)

        if len(population) < 2:
            break

    logger.info(f"survive = {len(population)}")
    for v in population.values():
        bot = v
    logger.info(f"winner = {bot.__dict__.__str__()}")
    logger.info("END")
