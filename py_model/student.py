from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from core.base import Base

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    age = Column(Integer)
    is_male = Column(Boolean)
    class_ = Column(String)