import threading, time
from apps.PC.utils.game import RunEnemy
from ml_model.face.fast_deepface import get_mood
from py_model.session import Session
from py_model.snapshote import GameSnapshotV1
from apps.PC.utils import game
from utils.game import frequency_key_down

"""
ЗАПУСКАЕТ ИГРЫ, ХРАНИТ В СЕБЕ ВСЕ СЦЕНАРИИ
И СОХРАНЯЕТ ВСЮ ИСТОРИЮ
"""

""" ДОП МЕТОДЫ """
def get_data_mood(session: Session):
    """Берёт данные настроения, частоты нажатия клавиш и записывает к студенту"""
    def snapshot():
        while True:
            emotion = get_mood()
            difficulty = get_difficulty()
            frequency_key_down = game.frequency_key_down()
            snapshot = GameSnapshotV1(emotion=emotion, game_different=difficulty, frequency_key_down=frequency_key_down)
            session.snapshots.append(snapshot)

            time.sleep(4)

    thread = threading.Thread(target=snapshot)
    thread.start()

def get_difficulty() -> int:
    """
    getter game different
    :return: int
    """
    summa = 0
    for enemy in game._enemies:
        if game.game_time() > enemy.begin_time_run:
            summa += enemy.speed
    return summa

""" СЦЕНАРИИ ИГР """
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


""" ТЕСТ """
if __name__ == '__main__':
    modul_my_errors_run()
