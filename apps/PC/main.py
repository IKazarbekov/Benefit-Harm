import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel, QTabWidget, \
    QStackedWidget, QStackedLayout, QFormLayout, QLineEdit, QSpinBox, QComboBox, QTableWidget, QTableWidgetItem, \
    QHBoxLayout
from student import StudentWindow
from py_model.student import Student
from py_model.dto.student import Student as DTOStudent
from apps.PC.utils import database, dto_mapper

class StartWindow(QMainWindow):
    def __init__(self):
        # Data
        database.connect()
        self.dto_students = dto_mapper.get_all_dto_students()
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

        button_student.clicked.connect(self.session_start_action)
        button_student.setEnabled(False)
        button_teacher.clicked.connect(lambda : self.stacked.setCurrentIndex(1))

        main_vbox = QVBoxLayout(self)
        main_vbox.addWidget(label)
        main_vbox.addWidget(button_student)
        main_vbox.addWidget(button_teacher)
        # endregion

        # region Teacher room
        teacher_label = QLabel("Кабинет учителя")
        teacher_label_table = QLabel("Ученики:")
        self.teacher_table = QTableWidget()
        self.teacher_table.setColumnCount(4)
        self.teacher_table.setHorizontalHeaderLabels(["Имя", "Класс",  "Последний сеанс", "Сеанс"])
        self.teacher_table.setColumnWidth(2, 180)
        teacher_button_add_student = QPushButton("Добавить ученика", self)
        teacher_button_add_student.clicked.connect(lambda : self.stacked.setCurrentIndex(2))

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

    """методы для кнопок"""
    def update_table_students(self):
        """
        update student table self.teacher_table: QTableWidget
        :return: None
        """
        students = self.dto_students

        self.teacher_table.setRowCount(len(students))
        for i, student in enumerate(students):

            def begin_session():
                self.session_start_action(student)

            button = QPushButton("начать")
            button.clicked.connect(begin_session)
            str_last_time = "Не было"
            if student.str_last_time_session:
                str_last_time = student.str_last_time_session
            label_last_session = QLabel(str_last_time)

            self.teacher_table.setCellWidget(i, 0, QLabel(student.name))
            self.teacher_table.setCellWidget(i, 1, QLabel(student.class_))
            self.teacher_table.setCellWidget(i, 2, label_last_session)
            self.teacher_table.setCellWidget(i, 3, button)

    def session_start_action(self, student = Student()):
        """
        :param student: student, which play session
        :return: None
        """
        self.window_student = StudentWindow(student)
        self.window_student.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.window_student.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.window_student.show()
        def close_window_of_student():
            database.add_object(self.window_student.session)
            database.add_objects(self.window_student.snapshots)
            database.save()
        self.window_student.destroyed.connect(close_window_of_student)

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
        self.stacked.setCurrentIndex(1)
        self.update_table_students()

# run
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    app.exit(app.exec())