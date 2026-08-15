import pygame, math, copy, time
from rich import color

"""МОДУЛЬ ИГРА
ОТВЕЧАЕТ ЗА ИГРОВОЙ ПРОЦЕСС
"""

# region КЛАССЫ
class GameObject:
    """Отвечает за отрисовку"""
    def __init__(self, x, y, color=(255, 0, 0), width = 100, height = 100, radius_circle = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.radius_circle = radius_circle
        self.color = color

    def draw(self, surface):
        if self.radius_circle is not None:
            pygame.draw.circle(surface, self.color, (self.rect.x, self.rect.y), self.radius_circle)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

class GameRunObject(GameObject):
    """Отвечает за здоровье и скорость"""
    def __init__(self, x, y, color=(255, 0, 0), health = 100, width = 100, height = 100, speed = 5):
        super().__init__(x, y, color, width, height)
        self.speed = speed
        self.health = health

class RunEnemy(GameRunObject):
    """Автоматически движущийся объект что отнимает здоровье игроку"""
    def __init__(self, x, y, color=(255, 0, 0), health=100, width=100, height=100, speed=5, points=None, begin_time_run = 0, removeInEnd: bool = True, circle:bool = False):
        super().__init__(x, y, color=color, health=health, width=width, height=height, speed=speed)

        # Список точек, по которым будет двигаться враг
        self.points = points if points else []
        self.current_point_index = 0  # Индекс текущей точки
        self.rect.x = x
        self.rect.y = y
        self.circle = circle
        self.removeInEnd = removeInEnd

        self.begin_time_run = begin_time_run

    def run(self):
        # Если нет точек или не пришло время — не двигаемся
        if not self.points or game_time() < self.begin_time_run:
            return

        # Если движение законченно
        if self.current_point_index == len(self.points):
            if self.circle:
                self.current_point_index = 0
            else:
                if self.removeInEnd:
                    _enemies.remove(self)
                return

        # Текущая целевая точка
        target_x, target_y = self.points[self.current_point_index]

        # Вектор от врага к цели
        dx = target_x - self.rect.x
        dy = target_y - self.rect.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            # Если почти достигли точки — переключаемся на следующую
            self.rect.x = target_x
            self.rect.y = target_y
            self.current_point_index = (self.current_point_index + 1)
        else:
            # Двигаемся к цели с нормализацией вектора
            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed

    def draw(self, surface):
        # Можно нарисовать врага
        pygame.draw.rect(surface, self.color, self.rect)

        # Для отладки — нарисовать маршрут
        if False and __debug__ and self.points:
            for point in self.points:
                pygame.draw.circle(surface, (255, 255, 0), (int(point[0]), int(point[1])), 5)

class Point(GameObject):
    """Очки на карте"""
    def __init__(self, x, y):
        super().__init__(x, y, "yellow", 50, 50, radius_circle=25)
# endregion

# region НАЧАЛЬНЫЕ НАСТРОЙКИ
# Размеры игрового мира (фиксированные)
_GAME_WIDTH = 1200
_GAME_HEIGHT = 800

# Начальный размер окна (для оконного режима)
_WINDOW_WIDTH = 1024
_WINDOW_HEIGHT = 768

# Переменные для текущих размеров экрана
screen_width = _WINDOW_WIDTH
screen_height = _WINDOW_HEIGHT
fullscreen = True  # начальный режим – оконный

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

mood = 0.0
# endregion

# region ИГРОВЫЕ ОБЪЕКТЫ
# игрок
player = GameRunObject(PLAYER_X, PLAYER_Y, color="gray", health=10, width=60, height=60)

# стены (в мировых координатах, они не зависят от размера окна)
walls = [
    pygame.Rect(100, 100, 1000, 20),     # Верхняя
    pygame.Rect(100, 580, 1000, 20),   # Нижняя
    pygame.Rect(100, 100, 20, 500),     # Левая
    pygame.Rect(1080, 100, 20, 500),   # Правая
]

# враги
BEGIN_ENEMIES = []
_enemies = []

# очки
BEGIN_POINTS = []
_points = []
# endregion

# region GAME METHODS
def draw(surface):
    """РИСОВАНИЕ КАДРА (на внутренней поверхности)"""
    # Фон
    surface.fill((0, 0, 0))

    # Игрок
    pygame.draw.rect(surface, player.color, player.rect)

    # Враги и очки и стены
    for wall in walls:
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

def control():
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
    for wall in walls:
        if player.rect.colliderect(wall):
            if dx > 0:
                player.rect.right = wall.left
            elif dx < 0:
                player.rect.left = wall.right
            break

    # Движение по Y
    player.rect.y += dy
    for wall in walls:
        if player.rect.colliderect(wall):
            if dy > 0:
                player.rect.bottom = wall.top
            elif dy < 0:
                player.rect.top = wall.bottom
            break

def game_logic():
    """Игровая логика - взаомодействие с объектами"""
    global mood
    # Управление игрока
    control()

    # Проверка столкновения с врагами и их движение
    for enemy in _enemies[:]:
        if player.rect.colliderect(enemy.rect):
            player.health -= 10
            _enemies.remove(enemy)
        enemy.run()

    # Проверка столкновения с очками
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

def restart_game():
    """СБОР/СБРОС ИГРЫ"""
    global _enemies, player, _begin_time, mood
    _begin_time = time.time()
    player = GameRunObject(PLAYER_X, PLAYER_Y, color="gray", health=10, width=60, height=60)
    mood = 0.0
    _enemies.clear()
    for enemy in BEGIN_ENEMIES:
        _enemies.append(copy.deepcopy(enemy))
    for point in BEGIN_POINTS:
        _points.append(copy.deepcopy(point))

def winner_game():
    """ПОБЕДА"""
    global _defeat_label_index
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
        pygame.quit()
        _running_game = False


def defeat_game():
    """ПРОИГРЫШ"""
    global _defeat_label_index, game_surface
    # Рисуем экран поражения на game_surface
    game_surface.fill((0, 0, 0))
    font = pygame.font.Font(None, 120)

    # Сообщение игроку
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
        restart_game()

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

def restart_screen():
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

def status() -> str:
    global _running_game, WINNING_CONDITION_FUNCTION
    if player.health <= 0:
        return "defeat"
    elif WINNING_CONDITION_FUNCTION():
        return "winner"
    else:
        return "gameplay"
# endregion

"""ЗАПУСК ИГРЫ"""
def run():
    global screen_width, screen_height, fullscreen, screen, game_surface, _running_game, _times_key_downs, _cps

    # Создаём окно (в оконном режиме)
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    game_surface = pygame.Surface((_GAME_WIDTH, _GAME_HEIGHT))
    pygame.display.set_caption("Benefit Harm")
    pygame.init()

    assert WINNING_CONDITION_FUNCTION is not None, "Не выстовленно условие выигрыша игры, установите функцию возвращающую bool в WINNING_CONDITION_FUNCTION()"

    restart_screen()
    restart_game()
    while _running_game:
        # --- Обработка событий ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _running_game = False

            # Переключение полноэкранного режима по F11
            if event.type == pygame.KEYDOWN:
                # statistic cps (frequency key down)
                now = time.time()
                _times_key_downs.append(now)
                _times_key_downs = [t for t in _times_key_downs if now - t <= 1.0]
                _cps = len(_times_key_downs)

                # full screen
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    restart_screen()

            # Изменение размера окна (только в оконном режиме)
            if event.type == pygame.VIDEORESIZE and not fullscreen:
                screen_width = event.w
                screen_height = event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)

        # --- Проверка здоровья и условия выигрыша ---
        if player.health <= 0:
            defeat_game()
        elif WINNING_CONDITION_FUNCTION():
            winner_game()
        else:
            game_logic()
            draw(game_surface)

        # --- Масштабирование и вывод на экран ---
        # Вычисляем масштаб с сохранением пропорций
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

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    WINNING_CONDITION_FUNCTION = lambda: False
    run()