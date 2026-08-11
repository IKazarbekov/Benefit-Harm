import threading, time
from apps.PC.utils.game import RunEnemy
from py_model.session import Session
from py_model.snapshote import GameSnapshotV1
from apps.PC.utils import game

"""
ЗАПУСКАЕТ ИГРЫ, ХРАНИТ В СЕБЕ ВСЕ СЦЕНАРИИ
И СОХРАНЯЕТ ВСЮ ИСТОРИЮ
"""

snapshots = []

""" ДОП МЕТОДЫ """
def collect_data_mood(session_id: int, snapshots: list, duration: int):
    """Берёт данные настроения, частоты нажатия клавиш и записывает к студенту
    :param session: Session
    :param duration: int
    :return: None
    """
    assert isinstance(session_id, int), "Неверный тип параметра снимков введён в функцию collect_data_mood()"
    assert isinstance(snapshots, list), "Неверный тип параметра снимков введён в функцию collect_data_mood()"
    assert isinstance(duration, int), "Неверный тип параметра интервала записи введён в функцию collect_data_mood()"
    assert duration > 0, "Неверное значение параметра интервала записи введён в функцию collect_data_mood()"

    from ml_model.face.fast_deepface import get_mood
    is_running = True
    def snapshot():
        while game._running_game:
            emotion = get_mood()
            difficulty = get_difficulty()
            frequency_key_down = game._cps
            health = game.player.health
            snapshot = GameSnapshotV1(session_id = session_id, emotion=emotion, game_different=difficulty, frequency_key_down=frequency_key_down, health=health)
            snapshots.append(snapshot)

            time.sleep(duration)

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
def modul_my_errors_run(session_id: int, snapshots: list, duration_snapshots: int) -> None:
    """
    Модуль игры - учимся на ошибках. Заучивание на ошибках от поведения враждебных объектов
    :param session: сеанс студента
    :param duration_snapshots: интервал записи снимков во время игры, если None то запись отключена
    :return: None
    """
    assert isinstance(snapshots, list), "Неверный тип параметра сеанса введён в функцию collect_data_mood()"
    assert isinstance(session_id, int), "Неверный тип параметра сеанса введён в функцию collect_data_mood()"
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
    game.WINNING_CONDITION_FUNCTION = lambda: game.game_time() > 50

    # enemy
    game.BEGIN_ENEMIES.append(RunEnemy(800, -400, width=200, height=200, speed=15, begin_time_run=5, points=(
        # круг 1
        (850, 150),
        (150, 150),
        (150, 350),
        (850, 350),
        # круг 2
        (850, 150),
        (150, 150),
        (150, 350),
        (850, 350),
        # диагональ
        (150, 150),
        (150, 350),
        (850, 350),
        # круг 1
        (850, 150),
        (150, 150),
        (150, 350),
        (850, 350),
        #уходит
        (1500, 150),
    ), circle=False))

    game.BEGIN_POINTS.append(game.Point(200, 200))
    game.BEGIN_POINTS.append(game.Point(300, 300))
    game.BEGIN_POINTS.append(game.Point(700, 500))
    game.BEGIN_POINTS.append(game.Point(900, 200))

    # player
    game.PLAYER_X = 500
    game.PLAYER_Y = 500

    # snapshots run
    if duration_snapshots is not None:
        collect_data_mood(session_id, snapshots, duration_snapshots)

    # run game
    game.run()

""" ТЕСТ """
if __name__ == '__main__':
    modul_my_errors_run(1, [], None)
