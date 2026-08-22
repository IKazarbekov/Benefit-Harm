import pygame, math
from typing import Callable

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

    def run(self, game_time: int|float) -> bool:
        """
        :param game_time: integer
        :return: bool - remove enemy ?
        """
        assert isinstance(game_time, (int, float))
        # Если нет точек или не пришло время — не двигаемся
        if not self.points or game_time < self.begin_time_run:
            return

        # Если движение законченно
        if self.current_point_index == len(self.points):
            if self.circle:
                self.current_point_index = 0
            else:
                if self.removeInEnd:
                    return True
                return False

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
    def __init__(self, x, y, assembled: Callable = lambda:None):
        super().__init__(x, y, "yellow", 50, 50, radius_circle=25)
        self.assembled = assembled

class Wall(GameObject):
    """Отвечает за препятствие"""
    """Доп. методов нет, только хранит данные"""
    def __init__(self, x, y, color=(255, 0, 0), width = 100, height = 100, radius_circle = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.radius_circle = radius_circle
        self.color = color
        super().__init__(x, y, color, width, height, radius_circle)
