import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QTabWidget, \
    QStackedWidget, QStackedLayout, QFormLayout, QLineEdit, QSpinBox, QComboBox, QTableWidget, QTableWidgetItem

from student import StudentWindow
from py_model.student import Student

import utils.data_students as data_students
import config


class StartWindow(QMainWindow):
    def __init__(self):
        # Data
        self.students = data_students.load_more_student(config.FILE_ALL_STUDENTS)

        # UI
        super().__init__()
        self.setWindowTitle("Benefit Harm Launcher 0.0.1")
        self.setFixedSize(800, 400)
        self.initUI()

    def initUI(self):
        """"""
        # region Main menu
        label = QLabel("Benefit Harm Launcher")
        button_student = QPushButton("Ученик", self)
        button_teacher = QPushButton("Учитель", self)

        button_student.clicked.connect(self.new_user_action)
        button_teacher.clicked.connect(lambda : self.stacked.setCurrentIndex(1))

        main_vbox = QVBoxLayout(self)
        main_vbox.addWidget(label)
        main_vbox.addWidget(button_student)
        main_vbox.addWidget(button_teacher)
        # endregion

        # region Teacher room
        teacher_label = QLabel("Кабинет учителя")
        self.teacher_table = QTableWidget()
        self.teacher_table.setColumnCount(4)
        teacher_button_add_student = QPushButton("Добавить ученика", self)
        teacher_button_add_student.clicked.connect(lambda : self.stacked.setCurrentIndex(2))

        teacher_vbox = QVBoxLayout()
        teacher_vbox.addWidget(teacher_label)
        teacher_vbox.addWidget(self.teacher_table)
        teacher_vbox.addWidget(teacher_button_add_student)

        self.update_table_students()
        # endregion

        # region Addendum student
        self.addendum_student_name = QLineEdit()
        self.addendum_student_cb = QComboBox(self)
        self.addendum_student_cb.addItems(["Мужской", "Женский"])
        self.addendum_student_sp = QSpinBox(minimum = 0)
        self.addendum_student_class = QLineEdit()

        addendum_student_label = QLabel("Добавить ученика")
        addendum_student_form = QFormLayout()
        addendum_student_form.addRow("ФИО", self.addendum_student_name)
        addendum_student_form.addRow("Возраст", self.addendum_student_sp)
        addendum_student_form.addRow("Пол", self.addendum_student_cb)
        addendum_student_form.addRow("Класс", self.addendum_student_class)
        addendum_student_button = QPushButton("Добавить")
        addendum_student_button.clicked.connect(self.add_student_action)

        addendum_student_vbox = QVBoxLayout()
        addendum_student_vbox.addWidget(addendum_student_label)
        addendum_student_vbox.addLayout(addendum_student_form)
        addendum_student_vbox.addWidget(addendum_student_button)
        # endregion

        # region Boxes
        screen_main = QWidget()
        screen_main.setLayout(main_vbox)
        screen_teacher = QWidget()
        screen_teacher.setLayout(teacher_vbox)
        screen_add_student = QWidget()
        screen_add_student.setLayout(addendum_student_vbox)

        self.stacked = QStackedLayout()
        self.stacked.addWidget(screen_main)
        self.stacked.addWidget(screen_teacher)
        self.stacked.addWidget(screen_add_student)

        central_widget = QWidget()
        central_widget.setLayout(self.stacked)
        self.setCentralWidget(central_widget)

        self.setStyleSheet("font-size:20px;")
        # endregion

    def update_table_students(self):
        students = self.students

        self.teacher_table.setRowCount(len(students))
        for i, student in enumerate(students):
            self.teacher_table.setCellWidget(i, 0, QLabel(student.name))
            self.teacher_table.setCellWidget(i, 1, QSpinBox(value=student.age))
            self.teacher_table.setCellWidget(i, 2, QLabel("" + student.is_male))
            self.teacher_table.setCellWidget(i, 3, QPushButton("Начать сеанс"))

    def new_user_action(self):
        student = Student(None, None, None)
        self.window_student = StudentWindow(student)
        self.window_student.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.window_student.show()

    def add_student_action(self):
        name = self.addendum_student_name.text()
        age = self.addendum_student_sp.value()
        male = self.addendum_student_cb.currentText()
        class_ = self.addendum_student_class.text()

        student = Student(name, age, male, class_)
        self.students.append(student)
        data_students.save(self.students, config.FILE_ALL_STUDENTS)

        self.stacked.setCurrentIndex(1)
        self.update_table_students()

# run
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    app.exit(app.exec())