import threading, time, cv2
from datetime import datetime
from apps.PC.utils.game import RunEnemy
from py_model.snapshote import GameSnapshotV1
from apps.PC.utils import game

"""
ЗАПУСКАЕТ ИГРЫ, ХРАНИТ В СЕБЕ ВСЕ СЦЕНАРИИ
И СОХРАНЯЕТ ВСЮ ИСТОРИЮ
"""

snapshots = []

""" ДОП МЕТОДЫ """
def collect_data_mood(session_id: int, snapshots: list, duration: float):
    """Берёт данные настроения, частоты нажатия клавиш и записывает к студенту
    :param session: Session
    :param duration: int
    :return: None
    """
    assert isinstance(session_id, int), "Неверный тип параметра снимков введён в функцию collect_data_mood()"
    assert isinstance(snapshots, list), "Неверный тип параметра снимков введён в функцию collect_data_mood()"
    assert isinstance(duration, float), "Неверный тип параметра интервала записи введён в функцию collect_data_mood()"
    assert duration > 0, "Неверное значение параметра интервала записи введён в функцию collect_data_mood()"

    def get_enemy_distance() -> int:
        player_rect = game.player.rect
        summa = 0
        for enemy in game._enemies:
            enemy_rect = enemy.rect
            distance = game.distance_between_rects(player_rect, enemy_rect)
            summa += distance
        return summa

    from ml_model.face.fast_deepface import get_mood
    camera = cv2.VideoCapture(0)
    is_running = True
    def snapshot():
        while game._running_game:
            emotion = get_mood(camera)
            difficulty = get_difficulty()
            frequency_key_down = game._cps
            health = game.player.health
            snapshot = GameSnapshotV1(session_id = session_id, emotion=emotion, game_different=difficulty, frequency_key_down=frequency_key_down, health=health, enemy_distance=get_enemy_distance(),
                                      status = game._status, count_defeat=game._count_defeat, time=datetime.now())
            snapshots.append(snapshot)

            time.sleep(duration)
        camera.release()

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
def modul_my_errors_run(session_id: int, snapshots: list, duration_snapshots: float) -> None:
    """
    Модуль игры - учимся на ошибках. Заучивание на ошибках от поведения враждебных объектов
    :param session: сеанс студента
    :param duration_snapshots: интервал записи снимков во время игры, если None то запись отключена
    :return: None
    """
    assert isinstance(snapshots, list), "Неверный тип параметра сеанса введён в функцию collect_data_mood()"
    assert isinstance(session_id, int), "Неверный тип параметра сеанса введён в функцию collect_data_mood()"

    # region Settings
    game.DEFEAT_LABEL = [
        "Первая ошибка",
        "Вторая ошибка",
        "Ошибки разные?",
        "Анализируй",
        "Пробуй другие пути",
        "И ты исправишь ошибку"
    ]
    game.DEFEAT_LABEL_REPEAT = False
    game.WINNING_CONDITION_FUNCTION = lambda: game.game_time() > 60
    # endregion
    # region Events
    def begin():
        game.add_object(game.Wall(300, 300, "white", 200, 200))
        game.add_object(game.Point(100, 200))
        game.add_object(game.Point(300, 200))
        game.add_object(game.Point(600, 200))
    game.add_event(game.GameEvent(begin, 0))
    # endregion
    # region Other
    # player
    game.PLAYER_X = 500
    game.PLAYER_Y = 500
    # snapshots run
    if duration_snapshots is not None:
        collect_data_mood(session_id, snapshots, duration_snapshots)
    # run game
    game.run()
    # endregion

""" ТЕСТ """
if __name__ == '__main__':
    modul_my_errors_run(1, [], None)
