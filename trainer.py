import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from itertools import combinations
from copy import deepcopy
from bot import ThresholdBot, ProbabilityBot
from gun import Gun
from core import RouletteCore


class Evolution:

    def __init__(self,
                 n_individuals: int,
                 bot_type: str,
                 pistol: Gun,
                 attenuation_coefficient: float,
                 n_fights: int,
                 mutation_settings: dict,
                 **logger_settings):
        self.__available_type = {'ThresholdBot': ThresholdBot,
                                 'ProbabilityBot': ProbabilityBot}
        self.logger = Logger(**logger_settings)
        if bot_type not in self.__available_type.keys():
            self.logger.write(f"Неверный тип бота: {bot_type}. "
                              f"Доступные типы: {', '.join(list(self.__available_type.keys()))}. "
                              f"Процесс остановлен.")
            self.logger.write('END')
            raise TypeError
        self.__bot_type = bot_type
        self.__n_individuals = n_individuals
        self.__pistol = pistol
        self.__attenuation_coefficient = attenuation_coefficient
        self.__n_fights = n_fights
        self.__mutation_settings = mutation_settings

    def init_population(self,
                        **bot_args
                        ) -> dict:
        """{имя_бота: бот}"""
        population = {}
        for i in range(self.__n_individuals):
            name = f"0.{i}"  # "номер_поколения.номер_бота"
            population[name] = self.__available_type[self.__bot_type](name=name, **bot_args)
        return population

    def _run_single_fight(self, pair_keys,
                          population: dict
                          ):
        k1, k2 = pair_keys
        sim = RouletteCore(
            gun=self.__pistol,
            players=[deepcopy(population[k1]), deepcopy(population[k2])],
            n_fights=self.__n_fights
        )
        return sim.fight()

    def selection(self, population: dict,
                  survive_threshold: float,
                  max_workers: int = None) -> tuple[dict, float]:
        pairs = list(combinations(population.keys(), 2))
        if not pairs:
            return deepcopy(population), survive_threshold * self.__attenuation_coefficient
        new_population = {}
        population_probs = []
        absolute_best_winner = None
        absolute_max_prob = -1.0
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._run_single_fight, pair, population)
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
            new_survive_threshold = self.__attenuation_coefficient * max(population_probs)
        else:
            new_survive_threshold = survive_threshold * self.__attenuation_coefficient
        return new_population, new_survive_threshold

    @staticmethod
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

    def mutation(self, population: dict) -> dict:
        if not self.__mutation_settings['use']:
            return population
        population_ = dict()
        for k, v in population.items():
            population_[k] = v
            population_[k].mutate(force=self.__mutation_settings['force'])
        return population_


class Logger:

    def __init__(self,
                 name: str,
                 path: str,
                 log_format: str,
                 max_bytes: int,
                 backup_count: int):
        self.__name = name
        self.__log_format = log_format
        self.__filename = f"{Path(path) / name}.log"
        self.__level = logging.DEBUG
        self.__max_bytes = max_bytes
        self.__backup_count = backup_count
        self.__logger = None
        self.__start()

    def __start(self):
        formatter = logging.Formatter(self.__log_format)
        file_handler = RotatingFileHandler(
                        filename=self.__filename,
                        maxBytes=self.__max_bytes,
                        backupCount=self.__backup_count,
                        encoding='utf-8'
                    )
        file_handler.setLevel(self.__level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.__level)
        console_handler.setFormatter(formatter)

        self.__logger = logging.getLogger(self.__name)
        self.__logger.setLevel(self.__level)
        self.__logger.addHandler(file_handler)
        self.__logger.addHandler(console_handler)

    def write(self, message: str):
        self.__logger.info(message)

