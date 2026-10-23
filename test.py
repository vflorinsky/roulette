import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from bot import RandomBot, ThresholdBot, ProbabilityBot
from gun import Gun
from core import RouletteCore

TEST_SETTINGS = {'n_fights': 10,
                 'gun': {'n_slots': 6},
                 'bots': {# 'ThresholdBot_1': {'threshold': 1, 'n_rotations': 3},
                          # 'ThresholdBot_2': {'threshold': 0, 'n_rotations': 3},
                          'RandomBot': {'n_rotations': 3},
                          'ProbabilityBot': {'n_rotations': 3,
                                             'n_slots': 6,
                                             'probs': [0.4178687111973717, 0.013624500473614859, 1, 0.5220252893473505, 0.41890325551401386, 0.4171216742168011, 0.9101932150881249, 0.8787717998419473, 0.07867651903534859, 0.2702861431254712, 0.08568612501846179, 0.3885546116369757, 0.9144354705059612, 0.10890457330871745, 0.11180504461988214, 0.14325939008942615, 0.6689663371913013]},
                          }
                 }
BOTS = {'RandomBot': RandomBot,
        'RandomBot_1': RandomBot,
        'RandomBot_2': RandomBot,
        'ThresholdBot': ThresholdBot,
        'ThresholdBot_1': ThresholdBot,
        'ThresholdBot_2': ThresholdBot,
        'ProbabilityBot': ProbabilityBot,
        'ProbabilityBot_1': ProbabilityBot,
        'ProbabilityBot_2': ProbabilityBot,
        }

LOG_SETTINGS = {'path': Path('logs') / 'test',
                'name': f"{'_vs_'.join(TEST_SETTINGS['bots'].keys())}",
                'format': '%(asctime)s - %(name)s - %(message)s',
                'maxBytes': 5 * 1024 * 1024,
                'backupCount': 3}


if __name__ == "__main__":

    # Инициализация
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

    pistol = Gun(n_slots=TEST_SETTINGS['gun']['n_slots'])
    players = [BOTS[bot_name](name=bot_name, **bot_opts) for bot_name, bot_opts in TEST_SETTINGS['bots'].items()]

    # Симуляция
    logger.info("START")
    logger.info(f"TEST_SETTINGS = {TEST_SETTINGS.__str__()}")

    simulator = RouletteCore(gun=pistol, players=players, n_fights=TEST_SETTINGS['n_fights'])
    stat = simulator.fight()

    logger.info(f"result = {stat.__str__()}")
    logger.info("END")


