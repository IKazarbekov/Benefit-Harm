import threading, time, cv2
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
                                      status = game._status)
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
    # region Enemies
    game.BEGIN_ENEMIES.append(RunEnemy(800, -400, width=200, height=200, speed=5, begin_time_run=15, points=(
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
    game.BEGIN_ENEMIES.append(RunEnemy(-100, -100, width=100, height=100, speed=5, begin_time_run=40,
                                       points=[(100 + i * 150, 150) if i % 2 == 0 else (100 + i * 150, 450) for i in range(10)], circle=True))
    # endregion
    # region Points
    game.BEGIN_POINTS.append(game.Point(200, 200))
    game.BEGIN_POINTS.append(game.Point(300, 300))
    game.BEGIN_POINTS.append(game.Point(700, 500))
    game.BEGIN_POINTS.append(game.Point(900, 200))
    # endregion
    def change_speed_enemies():
        if game._count_defeat < 2:
            game._enemies[0].speed += 10
        elif game._count_defeat < 4:
            game._enemies[0].speed += 5
    game.events.append(game.GameEvent(change_speed_enemies, 30, 10))
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
