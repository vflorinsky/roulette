import logging
from itertools import combinations
from concurrent.futures import ProcessPoolExecutor
from logging.handlers import RotatingFileHandler
from random import randint
from pathlib import Path
from bot import ThresholdBot, ProbabilityBot
from gun import Gun
from copy import deepcopy
from core import RouletteCore
from trainer import Logger


TRAINING_SETTINGS = {'n_generations': 2,
                  'start_volume': 2,
                  'n_fights': 1000,
                  'survive_threshold': 0.5,  # выживают те, что выше порога
                  'attenuation_coefficient': 1.0,  # коэффициент понижения порога выживаемости
                  'mutation': {'use': True,
                               'force': 15  # уровень шума в процентах от зашумляемого значения
                               },
                  'gun': {'n_slots': 6},
                  'training_bot_type': 'ThresholdBot',  # ProbabilityBot
                  'bot': {'ThresholdBot': {'n_rotations': 3,
                                           'threshold': randint(0, 6),
                                           'max_slots': 6},
                          'ProbabilityBot': {'n_rotations': 3,
                                             'max_slots': 6,
                                             'n_slots': 6}
                          }
                  }

LOG_SETTINGS = {'name': TRAINING_SETTINGS['training_bot_type'],
                'path': f"{Path('logs') / 'train'}",
                'log_format': '%(asctime)s - %(name)s - %(message)s',
                'max_bytes': 5 * 1024 * 1024,
                'backup_count': 3}

BOTS = {'ThresholdBot': ThresholdBot,
        'ProbabilityBot': ProbabilityBot}


def mutation(population: dict, force: float) -> dict:
    population_ = dict()
    for k, v in population.items():
        population_[k] = v
        population_[k].mutate(force=force)
    return population_


def init_population(n_individuals: int,
                    bot_type: str,
                    **bot_args
                    ) -> dict or None:
    """{имя_бота: бот}"""
    if bot_type not in BOTS.keys():
        logger.info(f"Неверный тип бота: {bot_type}. "
                    f"Доступные типы: {', '.join(list(BOTS.keys()))}. "
                    f"Процесс остановлен.")
        logger.info('END')
        return
    population = {}
    for i in range(n_individuals):
        name = f"0.{i}"  # "номер_поколения.номер_бота"
        population[name] = BOTS[bot_type](name=name, **bot_args)
    return population


def _run_single_fight(pair_keys,
                      population_data: dict,
                      pistol: Gun,
                      n_fights: int):
    k1, k2 = pair_keys
    sim = RouletteCore(
        gun=pistol,
        players=[deepcopy(population_data[k1]), deepcopy(population_data[k2])],
        n_fights=n_fights
    )
    return sim.fight()


def selection(population: dict,
              pistol: Gun,
              survive_threshold: float,
              attenuation_coefficient: float,
              n_fights: int,
              max_workers: int = None) -> tuple[dict, float]:
    pairs = list(combinations(population.keys(), 2))
    if not pairs:
        return deepcopy(population), survive_threshold * attenuation_coefficient
    new_population = {}
    population_probs = []
    absolute_best_winner = None
    absolute_max_prob = -1.0
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(_run_single_fight, pair, population, pistol, n_fights)
            for pair in pairs
        ]
        for future in futures:
            result = future.result()
            if not result:
                continue
            winner, max_probability = max(result.items(), key=lambda item: item[1])
            if max_probability > absolute_max_prob:
                absolute_max_prob = max_probability
                absolute_best_winner = winner
            if max_probability > survive_threshold:
                if winner not in new_population:
                    winner_copy = deepcopy(population[winner])
                    winner_copy.reset()
                    new_population[winner] = winner_copy
                population_probs.append(max_probability)
    if not new_population and absolute_best_winner is not None:
        winner_copy = deepcopy(population[absolute_best_winner])
        winner_copy.reset()
        new_population[absolute_best_winner] = winner_copy
        population_probs.append(absolute_max_prob)
    if population_probs:
        new_survive_threshold = attenuation_coefficient * max(population_probs)
    else:
        new_survive_threshold = survive_threshold * attenuation_coefficient
    return new_population, new_survive_threshold


def crossing(population: dict, generation: int) -> dict:
    new_population, bid, crossed = dict(), 0, []
    for k1 in population.keys():
        if k1 not in crossed:
            crossed.append(k1)
            new_population[k1] = deepcopy(population[k1])
            new_population[k1].reset()
        for k2 in population.keys():
            if k2 in crossed:
                continue
            name = f"{generation}.{bid}"
            bid += 1
            new_population[name] = population[k1].cross_with(individual=population[k2],
                                                             spring_name=name)
            new_population[name].max_slots(value=population[k1].max_slots())
    return new_population


if __name__ == "__main__":

    logger = Logger(**LOG_SETTINGS)

    logger.write("START")
    logger.write(f"TRAINING_SETTINGS = {TRAINING_SETTINGS.__str__()}")

    pistol = Gun(n_slots=TRAINING_SETTINGS['gun']['n_slots'])

    # Начальная популяция
    population = init_population(n_individuals=TRAINING_SETTINGS['start_volume'],
                                 bot_type=TRAINING_SETTINGS['training_bot_type'],
                                 **TRAINING_SETTINGS['bot'][TRAINING_SETTINGS['training_bot_type']]
                                 )
    if population is None:
        exit(0)
    survive_threshold = TRAINING_SETTINGS['survive_threshold']
    stop_message = "достигнуто максимальное число поколений"

    for generation in range(TRAINING_SETTINGS['n_generations']):
        logger.write(f"generation = {generation}")
        logger.write(f"volume = {len(population)}")
        logger.write(f"survive threshold = {survive_threshold}")

        # Отбор
        population, survive_threshold = selection(population=population,
                                                  pistol=pistol,
                                                  survive_threshold=survive_threshold,
                                                  attenuation_coefficient=TRAINING_SETTINGS['attenuation_coefficient'],
                                                  n_fights=TRAINING_SETTINGS['n_fights'])
        logger.write(f"volume after selection = {len(population)}")

        # Скрещивание
        population = crossing(population=population,
                              generation=generation + 1)
        logger.write(f"volume after crossing = {len(population)}")

        # Мутация
        if TRAINING_SETTINGS['mutation']['use']:
            population = mutation(population=population,
                                  force=float(TRAINING_SETTINGS['mutation']['force']))
            logger.write(f"volume after mutation = {len(population)}")
        logger.write('-' * 50)

        if len(population) < 2:
            stop_message = f"популяция сократилась до {len(population)}"
            break

    logger.write(f"stop reason = {stop_message}")
    logger.write(f"number of survived = {len(population)}")
    logger.write(f"survive threshold = {survive_threshold}")
    logger.write(f"survived bots:")
    for bot in population.values():
        logger.write(f"{bot.__dict__.__str__()}")
    logger.write("END")
