import os, json
from datetime import datetime
from enum import Enum
from py_model.student import Student

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Превращаем Enum в его значение
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

def load(file_name):
    if not os.path.exists(file_name):
        return None
    with open(file_name, "r", encoding="utf-8") as f:
        data = json.load(f)
    student = Student(**data)
    return student