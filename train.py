from random import randint
from pathlib import Path
from gun import Gun
from trainer import Evolution


TRAINING_SETTINGS = {'n_generations': 20,
                     'start_volume': 4,
                     'n_fights': 1000,
                     'survive_threshold': 0.5,  # выживают те, что выше порога
                     'attenuation_coefficient': 1.0,  # коэффициент понижения порога выживаемости
                     'mutation': {'use': True,
                                  'force': 15  # уровень шума в процентах от зашумляемого значения
                                  },
                     'gun': {'n_slots': 6},
                     'training_bot_type': 'ProbabilityBot',  # ThresholdBot
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


if __name__ == "__main__":

    pistol = Gun(n_slots=TRAINING_SETTINGS['gun']['n_slots'])
    evolution = Evolution(n_individuals=TRAINING_SETTINGS['start_volume'],
                          bot_type=TRAINING_SETTINGS['training_bot_type'],
                          pistol=pistol,
                          attenuation_coefficient=TRAINING_SETTINGS['attenuation_coefficient'],
                          n_fights=TRAINING_SETTINGS['n_fights'],
                          mutation_settings=TRAINING_SETTINGS['mutation'],
                          **LOG_SETTINGS)
    evolution.logger.write("START")
    evolution.logger.write(f"TRAINING_SETTINGS = {TRAINING_SETTINGS.__str__()}")

    # Начальная популяция
    population = evolution.init_population(
                                 **TRAINING_SETTINGS['bot'][TRAINING_SETTINGS['training_bot_type']]
                                 )
    survive_threshold = TRAINING_SETTINGS['survive_threshold']
    stop_message = "достигнуто максимальное число поколений"

    for generation in range(TRAINING_SETTINGS['n_generations']):
        evolution.logger.write(f"generation = {generation}")
        evolution.logger.write(f"volume = {len(population)}")
        evolution.logger.write(f"survive threshold = {survive_threshold}")

        # Отбор
        population, survive_threshold = evolution.selection(
            population=population,
            survive_threshold=survive_threshold)
        evolution.logger.write(f"volume after selection = {len(population)}")

        # Скрещивание
        population = evolution.crossing(population=population,
                                        generation=generation + 1)
        evolution.logger.write(f"volume after crossing = {len(population)}")

        # Мутация
        if TRAINING_SETTINGS['mutation']['use']:
            population = evolution.mutation(population=population)
            evolution.logger.write(f"volume after mutation = {len(population)}")
        evolution.logger.write('-' * 50)

        if len(population) < 2:
            stop_message = f"популяция сократилась до {len(population)}"
            break

    evolution.logger.write(f"stop reason = {stop_message}")
    evolution.logger.write(f"number of survived = {len(population)}")
    evolution.logger.write(f"survive threshold = {survive_threshold}")
    evolution.logger.write(f"survived bots:")
    for bot in population.values():
        evolution.logger.write(f"{bot.__dict__.__str__()}")
    evolution.logger.write("END")

