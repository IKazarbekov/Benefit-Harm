import pygame, math, copy, time
from _pytest import runner

"""МОДУЛЬ ИГРА
ОТВЕЧАЕТ ЗА ИГРОВОЙ ПРОЦЕСС
"""

"""КЛАССЫ"""
# Игровой объект
class GameObject:
    def __init__(self, x, y, color=(255, 0, 0), health = 100, width = 100, height = 100, speed = 5):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = speed
        self.health = health

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

# Движущийся враг
class RunEnemy(GameObject):
    def __init__(self, x, y, color=(255, 0, 0), health=100, width=100, height=100, speed=5, points=None, begin_time_run = 0):
        super().__init__(x, y, color=color, health=health, width=width, height=height, speed=speed)

        # Список точек, по которым будет двигаться враг
        self.points = points if points else []
        self.current_point_index = 0  # Индекс текущей точки
        self.rect.x = x
        self.rect.y = y

        self.begin_time_run = begin_time_run

    def run(self):
        if not self.points or game_time() < self.begin_time_run:
            return  # Если нет точек — не двигаемся

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
            self.current_point_index = (self.current_point_index + 1) % len(self.points)
        else:
            # Двигаемся к цели с нормализацией вектора
            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed

    def draw(self, surface):
        # Можно нарисовать врага
        pygame.draw.rect(surface, self.color, self.rect)

        # Для отладки — нарисовать маршрут
        if __debug__ and self.points:
            for point in self.points:
                pygame.draw.circle(surface, (255, 255, 0), (int(point[0]), int(point[1])), 5)

"""НАЧАЛЬНЫЕ НАСТРОЙКИ"""
pygame.init()

# Размеры игрового мира (фиксированные)
_GAME_WIDTH = 1200
_GAME_HEIGHT = 800

# Начальный размер окна (для оконного режима)
_WINDOW_WIDTH = 1024
_WINDOW_HEIGHT = 768

# Переменные для текущих размеров экрана
screen_width = _WINDOW_WIDTH
screen_height = _WINDOW_HEIGHT
fullscreen = False  # начальный режим – оконный

# Создаём окно (в оконном режиме)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
game_surface = pygame.Surface((_GAME_WIDTH, _GAME_HEIGHT))
pygame.display.set_caption("Benefit Harm")

clock = pygame.time.Clock()
FPS = 60
_begin_time = None
_running_game = True

# Меняющиеся переменные
_defeat_label_index = 0

"""НАСТРАИВАЕМЫЕ НАСТРОЙКИ"""
DEFEAT_LABEL = ["Вы проиграли"]
DEFEAT_LABEL_REPEAT = False

PLAYER_X, PLAYER_Y = 200, 200

WINNING_CONDITION_FUNCTION = None

"""ИГРОВЫЕ ОБЪЕКТЫ"""
# игрок
player = GameObject(PLAYER_X, PLAYER_Y, color="gray", health=10, width=60, height=60)

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
def add_enemy(points: tuple):
    assert isinstance(points, tuple)

    global _enemies

"""РИСОВАНИЕ КАДРА (на внутренней поверхности)"""
def draw(surface):
    # Фон
    surface.fill((0, 0, 0))

    # Игрок
    pygame.draw.rect(surface, player.color, player.rect)

    # Стены
    for wall in walls:
        pygame.draw.rect(surface, (255, 255, 255), wall)

    # Враги
    for enemy in _enemies:
        enemy.draw(surface)

    # Тексты (HP)
    font = pygame.font.SysFont("couriernew", 30, bold=False, italic=False)
    text = font.render(f"HP: {player.health}", True, (255, 255, 255))
    surface.blit(text, (100, 700))

"""ИГРОВАЯ ЛОГИКА"""
def game_logic():
    # --- Игровая логика ---
    # Управление
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:   dx = -player.speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  dx = +player.speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:     dy = -player.speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:   dy = +player.speed

    # Двигаем игрока
    player.rect.x += dx
    player.rect.y += dy

    # Проверка столкновения со стеной
    for wall in walls:
        if player.rect.colliderect(wall):
            player.rect.x -= dx
            player.rect.y -= dy
            break

    # Проверка столкновения с врагами и их движение
    for enemy in _enemies[:]:
        if player.rect.colliderect(enemy.rect):
            player.health -= 10
            _enemies.remove(enemy)
        enemy.run()

"""СБОР/СБРОС ИГРЫ"""
def restart_game():
    global _enemies, player, _begin_time
    _begin_time = time.time()
    player = GameObject(PLAYER_X, PLAYER_Y, color="gray", health=10, width=60, height=60)
    _enemies.clear()
    for enemy in BEGIN_ENEMIES:
        _enemies.append(copy.deepcopy(enemy))

"""ПОБЕДА"""
def winner_game():
    global _defeat_label_index
    # Рисуем экран поражения на game_surface
    game_surface.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)

    # Сообщение игроку
    text = font.render("Вы выиграли", True, (255, 0, 0))
    game_surface.blit(text, (_GAME_WIDTH // 2 - text.get_width() // 2, _GAME_HEIGHT // 2 - 50))

    restart_text = pygame.font.Font(None, 36).render("Нажмите R для выхода", True, (255, 255, 255))
    game_surface.blit(restart_text,
                      (_GAME_WIDTH // 2 - restart_text.get_width() // 2, _GAME_HEIGHT // 2 + 20))

    # Обработка перезапуска
    keys = pygame.key.get_pressed()
    if keys[pygame.K_r]:
        pygame.quit()

"""ПРОИГРЫШ"""
def defeat_game():
    global _defeat_label_index
    # Рисуем экран поражения на game_surface
    game_surface.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)

    # Сообщение игроку
    label = DEFEAT_LABEL[_defeat_label_index]
    text = font.render(label, True, (255, 0, 0))
    game_surface.blit(text, (_GAME_WIDTH // 2 - text.get_width() // 2, _GAME_HEIGHT // 2 - 50))

    restart_text = pygame.font.Font(None, 36).render("Нажмите R для перезапуска", True, (255, 255, 255))
    game_surface.blit(restart_text,
                      (_GAME_WIDTH // 2 - restart_text.get_width() // 2, _GAME_HEIGHT // 2 + 20))

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

"""СЛУЖЕБНЫЕ ФУНКЦИИ"""
def game_time():
    current_time = time.time()
    return current_time - _begin_time

"""ЗАПУСК ИГРЫ"""
def run():
    assert WINNING_CONDITION_FUNCTION is not None, "Не выстовленно условие выигрыша игры, установите функцию возвращающую bool в WINNING_CONDITION_FUNCTION()"

    global screen_width, screen_height, fullscreen, screen, _running_game

    restart_game()
    while _running_game:
        # --- Обработка событий ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Переключение полноэкранного режима по F11
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
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