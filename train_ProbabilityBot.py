import logging
from logging.handlers import RotatingFileHandler
from random import sample, uniform
from pathlib import Path
from bot import ProbabilityBot
from gun import Gun
from copy import deepcopy
from core import RouletteCore


TRAIN_SETTINGS = {'n_generations': 3,
                  'start_volume': 2,
                  'n_fights': 10000,
                  'mutation': {'use': True,
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


def mutation(population: dict, force: float) -> dict:
    population_ = dict()
    for k, v in population.items():
        population_[f"{k}.m"] = v
        new_probs = population_[f"{k}.m"].probabilites()
        for i in range(len(new_probs)):
            new_probs[i] += uniform(-0.01 * force * new_probs[i], 0.01 * force * new_probs[i])
        population_[f"{k}.m"].probabilites(value=new_probs)
    return population_


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
    new_population, bid, crossed = dict(), 0, []
    for k1 in population.keys():
        if k1 not in crossed:
            crossed.append(k1)
        for k2 in population.keys():
            if k2 in crossed:
                continue
            spring_probs = [0.5 * (a + b) for a, b in zip(population[k1].probabilites(), population[k2].probabilites())]
            name = f"{generation}.{bid}"
            bid += 1
            new_population[name] = ProbabilityBot(name=name,
                                                  n_rotations=n_rotations,
                                                  n_slots=n_slots)
            new_population[name].probabilites(value=spring_probs)
            new_population[name].reset()
            for k in [k1, k2]:
                if k not in new_population.keys():
                    new_population[k] = deepcopy(population[k])
                    new_population[k].reset()
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

        # Скрещивание
        population = crossing(population=population,
                              n_rotations=TRAIN_SETTINGS['bot']['n_rotations'],
                              generation=generation + 1,
                              n_slots=TRAIN_SETTINGS['bot']['n_rotations'])
        logger.info(f"volume after crossing = {len(population)}")

        # Мутация
        if TRAIN_SETTINGS['mutation']['use']:
            population = mutation(population=population,
                                  force=float(TRAIN_SETTINGS['mutation']['force']))
            logger.info(f"volume after mutation = {len(population)}")

        # # Отбор
        # population = selection(population=population, pistol=pistol)
        # logger.info(f"volume after selection = {len(population)}")
        logger.info('-' * 50)
        #
        # if len(population) < 2:
        #     break

    logger.info(f"survive = {len(population)}")
    for v in population.values():
        bot = v
    logger.info(f"winner = {bot.__dict__.__str__()}")
    logger.info("END")
