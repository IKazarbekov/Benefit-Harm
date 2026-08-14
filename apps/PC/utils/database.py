from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from py_model.student import Student
from py_model.session import Session
from core.base import Base
engine = None
db_session = None

def connect():
    global engine, db_session
    assert engine is None and db_session is None, "База данных уже подключена"
    engine = create_engine('sqlite:///apps/PC/data/students.db')
    DBSession = sessionmaker(bind=engine)
    db_session = DBSession()

def get_all(cls):
    assert db_session is not None, "Нет подключения к базе данных"
    assert issubclass(cls, Base), "1 параметр должен быть классом и унаследован от Base"
    return db_session.query(cls).all()

def add_object(object):
    assert db_session is not None, "Нет подключения к базе данных"
    assert isinstance(object, Base), "Передаваемый объект должен быть унаследовать от Base"
    db_session.add(object)

def add_objects(objects):
    assert db_session is not None, "Нет подключения к базе данных"
    assert isinstance(objects, (list, tuple)), "Передаваемый параметр должен быть списком или кортежём"
    for obj in objects:
        assert isinstance(obj, Base), "Передаваемые объекты должны быть унаследованы от Base"
    db_session.add_all(objects)

def get_last_session(student_id: int):
    return db_session.query(Session).filter_by(student_id=student_id).order_by(Session.begin_time.desc()).first()

def save():
    assert db_session is not None, "Нет подключения к базе данных"
    db_session.commit()

if __name__ == "__main__":
    engine = create_engine('sqlite:///../data/students.db')
    Session = sessionmaker(bind=engine)
    db_session = Session()

    # --- Создание объекта ---
    new_student = Student(
        name="Алексей",
        age=25,
        is_male=True,
        class_="11А"
    )

    # --- Сохранение в БД ---
    db_session.add(new_student)
    db_session.commit()