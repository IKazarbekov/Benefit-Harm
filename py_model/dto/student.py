from dataclasses import dataclass

@dataclass
class Student:
    db_id: int
    name: str
    class_: str
    str_last_time_session: str