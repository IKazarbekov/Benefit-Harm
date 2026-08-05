from dataclasses import dataclass, field
from typing import List
from py_model.session import Session

@dataclass
class Student:
    # begin data
    # this data must be failed in together during registration
    name: str
    age: int
    is_male: bool
    class_: str = None

    sessions: List[Session] = field(default_factory=list)