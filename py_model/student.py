from dataclasses import dataclass

@dataclass
class Student:
    # begin data
    # this data must be failed in together during registration
    name: str
    age: int
    male: bool