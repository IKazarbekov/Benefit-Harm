from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List
from py_model.mood import Mood

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
    snapshots: List = field(default_factory=list)