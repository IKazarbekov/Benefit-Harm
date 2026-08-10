from sqlalchemy import create_engine
from core.base import Base
from py_model.session import Session
from py_model.student import Student
from py_model.snapshote import GameSnapshotV1

PATH = r"""E:\projects\Benefit Harm\apps\PC\data\students.db"""
engine = create_engine('sqlite:///' + PATH)

# --- ВАЖНЫЙ ШАГ: Создаём все таблицы ---
Base.metadata.create_all(engine)

print("OK")

if __name__ == "__main__":
    pass