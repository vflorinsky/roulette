import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from bot import RandomBot, ThresholdBot, ProbabilityBot
from gun import Gun
from core import RouletteCore

TEST_SETTINGS = {'n_fights': 10000,
                 'gun': {'n_slots': 6},
                 'bots': {'RandomBot': {'n_rotations': 3},
                          'ThresholdBot': {'threshold': 0, 'n_rotations': 3},
                          # 'ProbabilityBot': {'n_rotations': 3,
                          #                    'n_slots': 6,
                          #                    # 'probs': [0.3342282898070752, 0.6784471528981466, 0.5978070005584111, 0.6566547561916868, 0.35104230970813743, 0.7317005630982257, 0.725000117252883, 0.8754982908740495, 0.5938431255093694, 0.1574896802701129, 1, 0.7752640624379565, 0.4058526106213022, 0.34195630681129163, 0.20397397125046526, 0.29624699385151626, 0.5224670636690136, 0.34691087811605326, 0.7171462381882202, 0.5886222438658828, 0.6225044410754517, 0.698942238567173, 0.9483078566317694, 0.37897741340012026, 0.5414362994155695, 0.3346048239134756, 0.837746634932496, 0.310287576749853, 0.34799471182554476, 0.5823061463509853, 0.6760738352029985, 0.3700175381569792, 0.3354191669892696, 0.1492533396803107, 0.6317542507136782, 0.42194522396623607, 0.20567892676341568, 0.4614110134241264, 0.42454739112786577, 0.8875260101876802, 0.42073788747861524]
                          #                    'probs': [0.4185478268921187, 0.7455516744430214, 0.8408586542202624, 0.3532215232690814, 0.6103112019611341, 0.3511231271935957, 0.3409706152630562, 0.44914211368300017, 0.4313287392108611, 0.5082800733584025, 0.2429346159344374, 0.32672971257072614, 0.5146509978127706, 0.6989829255010938, 0.7920422344951276, 0.3970790824245649, 0.34081339452669723, 0.833061797180818, 0.33890478675192376, 0.4131365923557873, 0.395970812938607, 0.3819871633359201, 0.5903554213507699, 0.710343360293204, 0.6254775984794106, 0.3839006770120489, 0.25104291472343504, 0.6801866710257445, 0.4738272240228625, 0.5010675708527752, 0.4391742257088504, 0.3301954118949278, 0.5201427616860754, 0.4665467328084169, 0.18066660350595076, 0.6339815299607019, 0.46683947717937657, 0.30393091170036735, 0.5286746807755188, 0.3541038935349009, 0.4986136540667118]
                          #                    },
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


