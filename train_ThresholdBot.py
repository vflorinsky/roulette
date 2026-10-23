import logging
from logging.handlers import RotatingFileHandler
from random import randint, choice, sample, uniform
from pathlib import Path
from bot import ThresholdBot
from gun import Gun
from copy import deepcopy
from statistics import median
from core import RouletteCore


TRAIN_SETTINGS = {'n_generations': 3,
                  'start_volume': 2,
                  'n_fights': 10000,
                  'survive_threshold': 0.0,  # выживают те, что выше порога
                  'attenuation_coefficient': 0.65,  # коэффициент понижения порога выживаемости
                  'mutation': {'use': True,
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


def mutation(population: dict, force: float) -> dict:
    population_ = dict()
    for k, v in population.items():
        population_[k] = v
        new_threshold = population_[k].threshold()
        new_threshold += uniform(-0.01 * force * new_threshold, 0.01 * force * new_threshold)
        population_[k].threshold(value=new_threshold)
    return population_


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


def selection(population: dict,
              pistol: Gun,
              survive_threshold: float,
              attenuation_coefficient: float) -> tuple[dict, float]:
    """
    :param population:
    :param pistol:
    :param survive_threshold:
    :param attenuation_coefficient:
    :return: (популяция, порог_выживаемости)
    """
    new_population, survive_probs, fighted, population_probs = dict(), dict(), [], []
    for k1 in population.keys():
        if k1 not in fighted:
            fighted.append(k1)
        for k2 in population.keys():
            if k2 in fighted:
                continue
            sim = RouletteCore(gun=pistol,
                               players=[deepcopy(population[k1]), deepcopy(population[k2])],
                               n_fights=TRAIN_SETTINGS['n_fights'])
            result = sim.fight()
            max_probability, winner = survive_threshold * attenuation_coefficient, None
            for k, v in result.items():
                if v > max_probability:
                    max_probability = v
                    winner = k
            if winner is not None:
                new_population[winner] = deepcopy(population[winner])
                new_population[winner].reset()
                population_probs.append(max_probability)
    return (new_population,
            sum(population_probs) / len(population_probs)) if len(
        population_probs) > 0 else survive_threshold * attenuation_coefficient


def crossing(population: dict, n_rotations: int, generation: int) -> dict:
    new_population, bid, crossed = dict(), 0, []
    for k1 in population.keys():
        if k1 not in crossed:
            crossed.append(k1)
            new_population[k1] = deepcopy(population[k1])
            new_population[k1].reset()
        for k2 in population.keys():
            if k2 in crossed:
                continue
            thrsh = 0.5 * (population[k1].threshold() + population[k1].threshold())
            name = f"{generation}.{bid}"
            bid += 1
            new_population[name] = ThresholdBot(name=name,
                                                n_rotations=n_rotations,
                                                threshold=thrsh)
            new_population[name].max_slots(value=population[k1].max_slots())
            new_population[name].threshold(value=thrsh)
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
    survive_threshold = TRAIN_SETTINGS['survive_threshold']
    stop_message = "достигнуто максимальное число поколений"

    for generation in range(TRAIN_SETTINGS['n_generations']):
        logger.info(f"generation = {generation}")
        logger.info(f"volume = {len(population)}")

        trsh = [v.threshold() for _, v in population.items()]

        logger.info(f"trsh mean = {sum(trsh) / len(trsh)}")
        logger.info(f"trsh median = {median(trsh)}")

        # Скрещивание
        population = crossing(population=population,
                              n_rotations=TRAIN_SETTINGS['bot']['n_rotations'],
                              generation=generation + 1)
        logger.info(f"volume after crossing = {len(population)}")

        # Мутация
        if TRAIN_SETTINGS['mutation']['use']:
            population = mutation(population=population,
                                  force=float(TRAIN_SETTINGS['mutation']['force']))
            logger.info(f"volume after mutation = {len(population)}")

        # Отбор
        population, survive_threshold = selection(population=population,
                                                  pistol=pistol,
                                                  survive_threshold=survive_threshold,
                                                  attenuation_coefficient=TRAIN_SETTINGS['attenuation_coefficient'])
        logger.info(f"volume after selection = {len(population)}")
        logger.info('-' * 50)

        if len(population) < 2:
            stop_message = "популяция сократилась до одной особи"
            break

    logger.info(f"stop reason = {stop_message}")
    logger.info(f"number of survived = {len(population)}")
    logger.info(f"survive threshold = {survive_threshold}")
    logger.info(f"survived bots:")
    for bot in population.values():
        logger.info(f"{bot.__dict__.__str__()}")
    logger.info("END")
