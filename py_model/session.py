from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Enum as SAEnum
from core.base import Base
from datetime import datetime
from enum import Enum
from py_model.mood import Mood

class Self_Assessment(Enum):
    VERY_HIGH = "Лучше всех"
    HIGH = "Лучший"
    AVERAGE = "Хороший"
    LOW = "Плохой"
    VERY_LOW = "Ужасный"

class Modul(Enum):
    ERROR = "Ошибка"

class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    mood = Column(SAEnum(Mood))           # храним значение Enum (например, Mood.GOOD.value)
    begin_time = Column(DateTime)         # datetime объект
    end_time = Column(DateTime)         # datetime объект
    self_assessment = Column(SAEnum(Self_Assessment)) # значение Self_Assessment
    modul = Column(SAEnum(Modul))          # значение Modul