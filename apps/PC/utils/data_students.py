import os, json, warnings
from datetime import datetime
from enum import Enum

from py_model.session import Session
from py_model.student import Student

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")  # Превращаем Enum в его значение
        if isinstance(obj, Enum):
            return obj.value  # Превращаем Enum в его значение
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return super().default(obj)

def save(student, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(student, f, cls=EnumEncoder, indent=4, ensure_ascii=False)

def load_one_student(file_name):
    warnings.warn("load_one_student is deprecated", DeprecationWarning)
    if not os.path.exists(file_name):
        return None
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
    student = Student(**data)
    return student

def load_more_student(file_name):
    if not os.path.exists(file_name):
        return None
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
    students = []
    for item in data:
        student = Student(**item)
        for i in range(len(student.sessions)):
            session_dict = student.sessions[i]
            session_dict["time"] = datetime.strptime(session_dict["time"], "%Y-%m-%d %H:%M:%S")
            student.sessions[i] = Session(**session_dict)
        students.append(student)
    return students