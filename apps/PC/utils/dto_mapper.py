from apps.PC.utils import database
from py_model import student as student_model
from py_model.dto import student as student_dto
from py_model.student import Student


def get_all_dto_students():
    origin_students = database.get_all(student_model.Student)
    dto_students = []
    for student in origin_students:
        last_session = database.get_last_session(student.id)
        last_session_time = None
        if last_session:
            last_session_time = str(last_session.begin_time)
        dto_student = student_dto.Student(student.id, student.name, student.class_, f"{last_session_time}")
        dto_students.append(dto_student)
    return dto_students

