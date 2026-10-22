import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from bot import RandomBot, ThresholdBot
from gun import Gun
from core import RouletteCore

TEST_SETTINGS = {'n_fights': 10000,
                 'gun': {'n_slots': 6},
                 'bots': {'ThresholdBot_1': {'threshold': 1, 'n_rotations': 3},
                          'ThresholdBot_2': {'threshold': 0, 'n_rotations': 3},
                          # 'RandomBot': {'n_rotations': 3},
                          }
                 }
BOTS = {'RandomBot': RandomBot,
        'RandomBot_1': RandomBot,
        'RandomBot_2': RandomBot,
        'ThresholdBot': ThresholdBot,
        'ThresholdBot_1': ThresholdBot,
        'ThresholdBot_2': ThresholdBot,
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


