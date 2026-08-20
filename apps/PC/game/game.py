import pygame, time, easypygamewidgets as epw
from py_model.game_status import Status
from apps.PC.game.game_objects import RunEnemy, Point, Wall, GameRunObject, GameObject
from apps.PC.game.game_event import GameEvent
"""
МОДУЛЬ ИГРА
ОТВЕЧАЕТ ЗА ИГРОВОЙ ПРОЦЕСС
"""
# region НАЧАЛЬНЫЕ НАСТРОЙКИ
# Размеры игрового мира (фиксированные), размер окна (для оконного режима), Переменные для текущих размеров экрана
_GAME_WIDTH = 1200
_GAME_HEIGHT = 800
_WINDOW_WIDTH = 1024
_WINDOW_HEIGHT = 768
screen_width = _WINDOW_WIDTH
screen_height = _WINDOW_HEIGHT
fullscreen = False

# Создаём окно (в оконном режиме)
screen = None
game_surface = None
pygame.display.set_caption("Benefit Harm")

clock = pygame.time.Clock()
FPS = 60
_begin_time = None
_running_game = True

# Меняющиеся переменные
_defeat_label_index = 0
# endregion

# region НАСТРАИВАЕМЫЕ НАСТРОЙКИ
DEFEAT_LABEL = ["Вы проиграли"]
DEFEAT_LABEL_REPEAT = False

PLAYER_X, PLAYER_Y = 200, 200

WINNING_CONDITION_FUNCTION = None
# endregion

# region СТАТИСТИКА
_times_key_downs = []
_cps = 0
_count_defeat = 0
_status = Status.GAMEPLAY

mood = 0.0
# endregion

# region ИГРОВЫЕ ОБЪЕКТЫ
player = GameRunObject(PLAYER_X, PLAYER_Y, color="gray", health=10, width=60, height=60)
_walls = [
    Wall(100, 100,"white", 1000, 20),
    Wall(100, 580,"white", 1000, 20),
    Wall(100, 100,"white", 20, 500),
    Wall(1080, 100,"white", 20, 500)
]
_enemies = []
_points = []
_events = []

# endregion

# region GAME METHODS
def _draw(surface):
    """РИСОВАНИЕ КАДРА (на внутренней поверхности)"""
    # Фон
    surface.fill((0, 0, 0))

    # Игрок
    pygame.draw.rect(surface, player.color, player.rect)

    # Враги и очки и стены
    for wall in _walls:
        pygame.draw.rect(surface, (255, 255, 255), wall)
    for enemy in _enemies:
        enemy.draw(surface)
    for point in _points:
        point.draw(surface)

    # Тексты (HP)
    font = pygame.font.SysFont("couriernew", 30, bold=False, italic=False)
    text = font.render(f"HP: {player.health}", True, (255, 255, 255))
    surface.blit(text, (100, 700))
    text = font.render(f"НАСТРОЙ: {mood * 100}%", True, (255, 255, 255))
    surface.blit(text, (300, 700))

def _control():
    global _times_key_downs, _cps
    """ УПРАВЛЕНИЕ И ДВИЖЕНИЕ ИГРОКА"""
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:   dx = -player.speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  dx = +player.speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:     dy = -player.speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:   dy = +player.speed

    # Движение по X
    player.rect.x += dx
    for wall in _walls:
        rect = wall.rect
        if player.rect.colliderect(rect):
            if dx > 0:
                player.rect.right = rect.left
            elif dx < 0:
                player.rect.left = rect.right
            break

    # Движение по Y
    player.rect.y += dy
    for wall in _walls:
        rect = wall.rect
        if player.rect.colliderect(rect):
            if dy > 0:
                player.rect.bottom = rect.top
            elif dy < 0:
                player.rect.top = rect.bottom
            break

def _game_logic():
    """Игровая логика - взаомодействие с объектами и события"""
    global mood, _events, _status
    # Проверка статуса
    if _status != Status.GAMEPLAY:
        _status = Status.GAMEPLAY

    # Управление игрока
    _control()

    # Проверка столкновения с врагами и их движение  и очками
    for enemy in _enemies[:]:
        if player.rect.colliderect(enemy.rect):
            player.health -= 10
            _enemies.remove(enemy)
        if enemy.run(game_time()):
            _enemies.remove(enemy)
    for point in _points[:]:
        if player.rect.colliderect(point.rect):
            _points.remove(point)
            mood += 0.3
            player.speed *= 1.2
            if mood < 0.3:
                player.color = "gray"
            elif mood < 0.6:
                player.color = "orange"
            else:
                player.color = "yellow"

    # Проверка и вызов событий
    for event in _events:
        if event.enable and game_time() >= event.time_run:
            event.func()
            if event.duration is None:
                event.enable = False
            else:
                event.time_run += event.duration

def _restart_game():
    """СБОР/СБРОС ИГРЫ"""
    global _enemies, player, _begin_time, mood
    _begin_time = time.time()
    player = GameRunObject(PLAYER_X, PLAYER_Y, color="gray", health=10, width=60, height=60)
    mood = 0.0
    _enemies.clear()
    _points.clear()

def _winner_game():
    """ПОБЕДА"""
    global _defeat_label_index, _running_game, _status

    # Статус игры
    if _status != Status.WINNER:
        _status = Status.WINNER
    # Рисуем экран поражения на game_surface
    game_surface.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)

    # Сообщение игроку
    text = font.render("Вы выиграли", True, (0, 255, 0))
    game_surface.blit(text, (_GAME_WIDTH // 2 - text.get_width() // 2, _GAME_HEIGHT // 2 - 50))

    restart_text = pygame.font.Font(None, 36).render("Нажмите R для выхода", True, (255, 255, 255))
    game_surface.blit(restart_text,
                      (_GAME_WIDTH // 2 - restart_text.get_width() // 2, _GAME_HEIGHT // 2 + 20))

    # Обработка перезапуска
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        _running_game = False

def _defeat_game():
    """ПРОИГРЫШ"""
    global _defeat_label_index, game_surface, _status, _count_defeat
    # Statistic and one run
    if _status != Status.DEFEAT:
        _status = Status.DEFEAT
        _count_defeat += 1
        epw.Button(text="Перезапуск").place(500, 500)
    # Рисуем экран поражения на game_surface
    game_surface.fill((0, 0, 0))
    font = pygame.font.Font(None, 120)
    label = DEFEAT_LABEL[_defeat_label_index]
    text = font.render(label, True, (255, 0, 0))
    game_surface.blit(text, (_GAME_WIDTH // 2 - text.get_width() // 2, _GAME_HEIGHT // 2 - 50))
    restart_text = pygame.font.Font(None, 40).render("Нажмите R для перезапуска", True, (255, 255, 255))
    game_surface.blit(restart_text,
                      (_GAME_WIDTH // 2 - restart_text.get_width() // 2, _GAME_HEIGHT // 2 + 50))
    # Обработка перезапуска
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        # defeat label
        _defeat_label_index += 1
        if _defeat_label_index == len(DEFEAT_LABEL):
            if DEFEAT_LABEL_REPEAT: _defeat_label_index = 0
            else: _defeat_label_index = len(DEFEAT_LABEL) - 1
        # restart game data
        _restart_game()

# Служебные методы

def distance_between_rects(rect1: pygame.Rect, rect2: pygame.Rect) -> float:
    """
    Вычисляет расстояние между двумя прямоугольниками по ближайшим краям
    (по осям X и Y, возвращает евклидово расстояние).
    """
    assert isinstance(rect1, pygame.Rect)
    assert isinstance(rect2, pygame.Rect)
    # Расстояние по оси X (между ближайшими краями)
    if rect1.right < rect2.left:
        dx = rect2.left - rect1.right
    elif rect2.right < rect1.left:
        dx = rect1.left - rect2.right
    else:
        dx = 0  # Проекции перекрываются по X

    # Расстояние по оси Y (между ближайшими краями)
    if rect1.bottom < rect2.top:
        dy = rect2.top - rect1.bottom
    elif rect2.bottom < rect1.top:
        dy = rect1.top - rect2.bottom
    else:
        dy = 0  # Проекции перекрываются по Y

    # Евклидово расстояние
    import math
    return math.hypot(dx, dy)

def game_time():
    """СЛУЖЕБНЫЕ ФУНКЦИИ"""
    current_time = time.time()
    return current_time - _begin_time

def _restart_screen():
    "Для обновления полноэкранного режима"
    global fullscreen, screen_width, screen_height, screen
    if fullscreen:
        # Полноэкранный режим
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
    else:
        # Оконный режим
        screen_width = _WINDOW_WIDTH
        screen_height = _WINDOW_HEIGHT
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

def add_object(obj: GameObject):
    assert isinstance(obj, GameObject)

    if isinstance(obj, Wall):
        _walls.append(obj)
    elif isinstance(obj, RunEnemy):
        _enemies.append(obj)
    elif isinstance(obj, Point):
        _points.append(obj)

def add_objects(objects: list[GameObject]):
    assert isinstance(objects, list)
    for obj in objects:
        add_object(obj)

def add_event(event: GameEvent):
    assert isinstance(event, GameEvent)
    _events.append(event)
# endregion

"""ЗАПУСК ИГРЫ"""
def run():
    global screen_width, screen_height, fullscreen, screen, game_surface, _running_game, _times_key_downs, _cps

    # Init window
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    game_surface = pygame.Surface((_GAME_WIDTH, _GAME_HEIGHT))
    pygame.display.set_caption("Benefit Harm")
    pygame.init()
    epw.link_pygame_window(screen)

    assert WINNING_CONDITION_FUNCTION is not None, "Не выстовленно условие выигрыша игры, установите функцию возвращающую bool в WINNING_CONDITION_FUNCTION()"

    _restart_screen()
    _restart_game()
    while _running_game:
        # region Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _running_game = False
                break

            # Window size
            if event.type == pygame.KEYDOWN:
                # statistic cps (frequency key down)
                now = time.time()
                _times_key_downs.append(now)
                _times_key_downs = [t for t in _times_key_downs if now - t <= 1.0]
                _cps = len(_times_key_downs)

                # full screen
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    _restart_screen()
            if event.type == pygame.VIDEORESIZE and not fullscreen:
                screen_width = event.w
                screen_height = event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

            # Library epw
            epw.handle_event(event)
        # endregion

        # region Winner and defeat
        if player.health <= 0:
            _defeat_game()
        elif WINNING_CONDITION_FUNCTION():
            _winner_game()
        else:
            _game_logic()
            _draw(game_surface)
        # endregion

        # region Screen update
        scale_x = screen_width / _GAME_WIDTH
        scale_y = screen_height / _GAME_HEIGHT
        scale = min(scale_x, scale_y)

        new_width = int(_GAME_WIDTH * scale)
        new_height = int(_GAME_HEIGHT * scale)

        # Масштабируем поверхность
        scaled_surface = pygame.transform.scale(game_surface, (new_width, new_height))

        # Центрируем на экране
        offset_x = (screen_width - new_width) // 2
        offset_y = (screen_height - new_height) // 2

        # Заливаем экран чёрным (поля)
        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (offset_x, offset_y))

        # Library epw
        epw.flip()

        pygame.display.flip()
        clock.tick(FPS)
        # endregion

    pygame.quit()

if __name__ == "__main__":
    WINNING_CONDITION_FUNCTION = lambda: False
    run()