from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum
from core.base import Base
from datetime import datetime
from py_model.game_status import Status

class GameSnapshotV1(Base):
    __tablename__ = 'game_snapshots_v1'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    emotion = Column(String)              # хранит значение Mood (строка)
    frequency_key_down = Column(Integer)
    game_different = Column(Integer)
    health = Column(Integer)
    time = Column(DateTime, default=datetime.now)
    enemy_distance = Column(Integer)
    status = Column(SAEnum(Status))
    count_defeat = Column(Integer)