import sys, functools

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QStackedLayout, \
    QFormLayout, QLineEdit, QSpinBox, QComboBox, QTableWidget, QHBoxLayout
from py_model.session import Session
from py_model.student import Student
from py_model.dto.student import Student as DTOStudent
from apps.PC.utils import database, dto_mapper
import game_launcher
from datetime import datetime

class StartWindow(QMainWindow):
    def __init__(self):
        # Data
        database.connect()
        self.dto_students = dto_mapper.get_all_dto_students()
        # UI
        super().__init__()
        self.setWindowTitle("Benefit Harm Launcher")
        self.setWindowIcon(QIcon("apps/PC/icon.png"))
        self.setMinimumSize(700, 350)
        self.initUI()

    def initUI(self):
        """"""
        # region Main menu
        label = QLabel("Benefit Harm Launcher")
        button_teacher = QPushButton("Начать", self)
        button_teacher.clicked.connect(lambda : self.stacked.setCurrentWidget(self.screen_teacher))

        main_vbox = QVBoxLayout(self)
        main_vbox.addWidget(label)
        main_vbox.addWidget(button_teacher)
        # endregion

        # region Teacher room
        teacher_label = QLabel("Кабинет учителя")
        teacher_label_table = QLabel("Ученики:")
        self.teacher_table = QTableWidget()
        self.teacher_table.setColumnCount(5)
        self.teacher_table.setHorizontalHeaderLabels(["Имя", "Класс",  "Последний сеанс", "Сеанс", "Данные"])
        self.teacher_table.setColumnWidth(2, 180)
        self.teacher_table.setColumnWidth(3, 140)
        self.teacher_table.setColumnWidth(4, 140)
        teacher_button_add_student = QPushButton("Добавить ученика", self)
        teacher_button_add_student.clicked.connect(lambda : self.stacked.setCurrentWidget(self.screen_add_student))

        teacher_vbox = QVBoxLayout()
        teacher_vbox.addWidget(teacher_label)
        teacher_vbox.addWidget(teacher_label_table)
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
        addendum_student_back = QPushButton("Назад")
        addendum_student_back.setFixedWidth(100)
        addendum_student_back.clicked.connect(lambda: self.stacked.setCurrentWidget(self.screen_teacher))
        addendum_student_form = QFormLayout()
        addendum_student_form.addRow("ФИО", self.addendum_student_name)
        addendum_student_form.addRow("Возраст", self.addendum_student_sp)
        addendum_student_form.addRow("Пол", self.addendum_student_cb)
        addendum_student_form.addRow("Класс", self.addendum_student_class)
        addendum_student_button = QPushButton("Добавить")
        addendum_student_button.clicked.connect(self.add_student_action)

        addendum_student_vbox = QVBoxLayout()
        addendum_student_vbox.addWidget(addendum_student_label)
        addendum_student_vbox.addWidget(addendum_student_back)
        addendum_student_vbox.addLayout(addendum_student_form)
        addendum_student_vbox.addWidget(addendum_student_button)
        # endregion

        # region Student data
        student_data_label = QLabel("Данные студента")
        student_data_button_back = QPushButton("Назад")
        student_data_button_back.setFixedWidth(150)
        student_data_button_back.clicked.connect(lambda: self.stacked.setCurrentWidget(self.screen_teacher))
        self.student_data_form = QFormLayout()

        student_data_vbox = QVBoxLayout()
        student_data_vbox.addWidget(student_data_label)
        student_data_vbox.addWidget(student_data_button_back)
        student_data_vbox.addLayout(self.student_data_form)
        # endregion

        # region Boxes
        self.screen_main = QWidget()
        self.screen_main.setLayout(main_vbox)
        self.screen_teacher = QWidget()
        self.screen_teacher.setLayout(teacher_vbox)
        self.screen_add_student = QWidget()
        self.screen_add_student.setLayout(addendum_student_vbox)
        self.screen_student_data = QWidget()
        self.screen_student_data.setLayout(student_data_vbox)

        self.stacked = QStackedLayout()
        self.stacked.addWidget(self.screen_main)
        self.stacked.addWidget(self.screen_teacher)
        self.stacked.addWidget(self.screen_add_student)
        self.stacked.addWidget(self.screen_student_data)

        central_widget = QWidget()
        central_widget.setLayout(self.stacked)
        self.setCentralWidget(central_widget)

        self.setStyleSheet("font-size:20px;")
        # endregion

    """методы для кнопок"""
    def update_table_students(self):
        """
        update student table self.teacher_table: QTableWidget
        :return: None
        """
        students = self.dto_students

        def begin_session(student_id: int):
            origin_student = database.get_student(student_id)
            self.session_start_action(origin_student)
        self.teacher_table.setRowCount(len(students))
        for i, student in enumerate(students):

            button_session = QPushButton("Начать")
            button_session.clicked.connect(functools.partial(begin_session, student.db_id))
            button_data = QPushButton("Посмотреть")
            button_data.clicked.connect(lambda: self.stacked.setCurrentWidget(self.screen_student_data))
            str_last_time = "Не было"
            if student.str_last_time_session:
                str_last_time = student.str_last_time_session
            label_last_session = QLabel(str_last_time)

            self.teacher_table.setCellWidget(i, 0, QLabel(student.name))
            self.teacher_table.setCellWidget(i, 1, QLabel(student.class_))
            self.teacher_table.setCellWidget(i, 2, label_last_session)
            self.teacher_table.setCellWidget(i, 3, button_session)
            self.teacher_table.setCellWidget(i, 4, button_data)

    def session_start_action(self, student: Student):
        """
        :param student: student, which play session
        :return: None
        """
        # begin data
        session = Session(student_id = student.id, begin_time=datetime.now())
        database.add_object(session)
        database.save()
        snapshots = []

        # gameplay
        game_launcher.modul_one(session.id, snapshots, 0.2)

        # end data
        session.end_time = datetime.now()
        database.add_objects(snapshots)
        database.save()

    def add_student_action(self):
        """
        Add new student in list - self.students, from screen addendum_student
        :return: None
        """
        assert self.stacked.currentIndex() == 2

        name = self.addendum_student_name.text()
        age = self.addendum_student_sp.value()
        is_male = self.addendum_student_cb.currentText() == "Мужской"
        class_ = self.addendum_student_class.text()

        new_student = Student(
            name=name,
            age=age,
            is_male=is_male,
            class_= class_
        )
        database.add_object(new_student)
        database.save()
        new_dto_student = DTOStudent(
            db_id=new_student.id,
            name=new_student.name,
            class_=new_student.class_,
            str_last_time_session="не было"
        )
        self.dto_students.append(new_dto_student)
        self.stacked.setCurrentWidget(self.screen_teacher)
        self.update_table_students()

    def watch_student_data(self):
        pass

# run
if __name__ == '__main__':
    import ctypes
    myappid = 'mycompany.myproduct.myapp'  # Вы можете использовать любое уникальное имя
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    app.exit(app.exec())