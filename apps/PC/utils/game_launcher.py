import game
from game import RunEnemy

"""
ЗАПУСКАЕТ ИГРЫ, ХРАНИТ В СЕБЕ ВСЕ СЦЕНАРИИ
И СОХРАНЯЕТ ВСЮ ИСТОРИЮ
"""

def modul_my_errors_run():
    # defeat and winner game settings
    game.DEFEAT_LABEL = [
        "Первая ошибка",
        "Вторая ошибка",
        "Ошибки разные?",
        "Анализируй",
        "Пробуй другие пути",
        "И ты исправишь ошибку"
    ]
    game.DEFEAT_LABEL_REPEAT = False
    game.WINNING_CONDITION_FUNCTION = lambda: game.game_time() > 20

    # enemy
    game.BEGIN_ENEMIES.append(RunEnemy(800, -400, width=200, height=200, speed=10, begin_time_run=10, points=(
        (850, 150),
        (150, 150),
        (150, 350),
        (850, 350),
        (850, 150),
        (150, 150),
        (150, 350),
        (850, 350),
        (150, 150),
        (150, 350),
        (850, 350),
    )))

    # player
    game.PLAYER_X = 500
    game.PLAYER_Y = 500

    # run game
    game.run()

if __name__ == '__main__':
    modul_my_errors_run()