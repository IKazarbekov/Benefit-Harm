import os, json
from py_model.student import Student

file_name = r"data\students.json"

def save(student):
    with open(file_name, "w") as f:
        json.dump(students, f)

def open(student):
    global students
    with open(file_name, "r") as f:
        students = json.load(f)