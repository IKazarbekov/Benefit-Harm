import pygame

"""МОДУЛЬ ИГРА
ОТВЕЧАЕТ ЗА ИГРОВОЙ ПРОЦЕСС
"""

"""КЛАССЫ"""
# Враждебный объект
class GameObject:
    def __init__(self, x, y, color=(255, 0, 0)):
        self.rect = pygame.Rect(x, y, 100, 100)
        self.color = color
        self.speed = 2
        self.health = 100

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        screen.fill(self.color, self.rect)

"""НАЧАЛЬНЫЕ НАСТРОЙКИ"""
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
size = width, height = (1200, 800)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("My game")
fpsClock=pygame.time.Clock()
fps = 60
pygame.init()

"""ИГРОВЫЕ ОБЪЕКТЫ"""
# игрок
player = GameObject(200, 200)

# cтены
walls = [
    pygame.Rect(100, 100, 1000, 20),     # Верхняя
    pygame.Rect(100, 580, 1000, 20),   # Нижняя
    pygame.Rect(100, 100, 20, 500),     # Левая
    pygame.Rect(1080, 100, 20, 500),   # Правая
]

# враги
enemies = []
enemies.append(GameObject(400, 400))

"""РИСОВАНИЕ КАДРА"""
def draw():
    # Фон
    screen.fill((0, 0, 0))

    # Игрок
    screen.fill(player.color, player.rect)

    # Стены
    for wall in walls:
        screen.fill((255, 255, 255), wall)

    # Враги
    for enemy in enemies:
        enemy.draw()

    # Тексты
    font = pygame.font.SysFont("couriernew", 30, bold=False, italic=False)
    text = font.render(f"HP: {player.health}", 30, (255, 255, 255))
    screen.blit(text, (100, 700))

"""ЗАПУСК ИГРЫ"""
def run():
    """ИГРОВОЙ ЦИКЛ"""
    running = True
    while running:
        # Обработчик событий
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # Проверка здоровья
        if player.health <= 0:
            # ПРОИГРЫШ
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 74)
            text = font.render("Вы проиграли!", True, (255, 0, 0))
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - 50))

            restart_text = pygame.font.Font(None, 36).render("Нажмите R для перезапуска", True, (255, 255, 255))
            screen.blit(restart_text,
                        (screen.get_width() // 2 - restart_text.get_width() // 2, screen.get_height() // 2 + 20))
        else:
            # ИГРА ПРОДОЛЖАЕТСЯ

            # Управление
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:   dx = -player.speed
            if keys[pygame.K_RIGHT]:  dx = +player.speed
            if keys[pygame.K_UP]:     dy = -player.speed
            if keys[pygame.K_DOWN]:   dy = +player.speed

            # Двигаем игрока
            player.rect.x += dx
            player.rect.y += dy

            # Проверка столкновения со стеной
            for wall in walls:
                if player.rect.colliderect(wall):
                    player.rect.x -= dx
                    player.rect.y -= dy
                    break  # Если столкнулся с одной стеной — дальше не проверяем

            # Проверка столкновения к врагом
            for enemy in enemies[:]:  # Используем копию списка
                if player.rect.colliderect(enemy.rect):
                    # Игрок получает урон
                    player.health -= 10
                    enemies.remove(enemy)  # Враг исчезает
                    print(player.health)
        # Кадр
        draw()
        fpsClock.tick(60)
        pygame.display.flip()

    while pygame.event.wait().type != pygame.QUIT:
        pygame.display.flip()

    pygame.quit()