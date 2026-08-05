from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class Mood(Enum):
    JOY = "Радость"
    ANGER = "Гнев"
    SADNESS = "Печаль"
    GOOD = "Спокойный"

class Self_Assessment(Enum):
    VERY_HIGH = "Лучше всех"
    HIGH = "Лучший"
    AVERAGE = "Хороший"
    LOW = "Плохой"
    VERY_LOW = "Ужасный"

class Modul(Enum):
    ERROR = "Ошибка"

@dataclass
class Session:
    mood: Mood = None
    time: datetime = None
    self_assessment: Self_Assessment = None
    modul: Modul = None