from enum import EnumMeta
from utils import game_launcher
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QApplication, QStackedLayout, \
    QStackedWidget, QFormLayout, QLineEdit, QSpinBox, QComboBox
from prometheus_client import Enum
from win32ctypes.pywin32.pywintypes import datetime

import utils.camera as camera
from ml_model.face import fast_insighface
from py_model import student
from typing import Callable
from py_model.session import Session, Self_Assessment
from py_model.mood import Mood
import config

class StudentWindow(QMainWindow):
    def __init__(self, student, allow_camera: bool = False):
        # data
        self.student = student
        self.session = None
        self.snapshots = []
        self.allow_camera = allow_camera

        # UI
        super().__init__()
        self.initUI()
        if self.student is None:
            self.show_message("Я Benefit Harm", "Давай познакомимся !", "Начать", self.begin_register)
        else:
            self.show_message("Benefit Harm", "Давно не виделись !", "Начать", self.begin_session)

    def initUI(self):
        """
        initialization UI
        :return: None
        """

        # region SCREEN TITLE
        """
        one title and one button
        message_show() - for call screen title
        """
        # widgets
        self.message_label = QLabel("Benefit Harm", self)
        self.message_text = QLabel("Вы готовы?", self)
        self.message_button = QPushButton("начать сеанс", self)

        # styles
        self.message_label.setStyleSheet("font-size:20px;")
        self.message_button.setStyleSheet("font-size:20px;")

        # boxes
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.message_label)
        vbox.addWidget(self.message_text)
        vbox.addWidget(self.message_button)
        # endregion

        # region SCREEN FORM
        """
        many questions
        """
        #widgets
        self.form_label = QLabel("тема", self)
        self.form_layout = QFormLayout()
        self.form_button = QPushButton("готово", self)

        # boxes
        self.form_vbox = QVBoxLayout(self)
        self.form_vbox.addWidget(self.form_label)
        self.form_vbox.addLayout(self.form_layout)
        self.form_vbox.addWidget(self.form_button)
        # endregion

        # region CONTAINERS
        # screens
        screen_begin = QWidget()
        screen_form = QWidget()
        screen_begin.setLayout(vbox)
        screen_form.setLayout(self.form_vbox)

        # central widget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        self.stacked_widget.addWidget(screen_begin)
        self.stacked_widget.addWidget(screen_form)
        # endregion

    """МЕТОДЫ ДЛЯ РАБОТЫ С ЭКРАНАМИ ОКНА"""

    def show_message(self, label: str, message: str, button_label: str, action: Callable) -> None:
        """
        For show one message
        :param label: big label
        :param message: small label
        :param button_label: text in button
        :return: None
        """
        assert isinstance(label, str), "Неверный тип 1 параметра метода"
        assert isinstance(message, str), "Неверный тип 2 параметра метода"
        assert isinstance(button_label, str), "Неверный тип 3 параметра метода"
        assert isinstance(action, Callable), "Неверный тип 4 параметра метода"

        # action
        self.disconnect_clicked_button(self.message_button)
        self.message_button.clicked.connect(action)

        # ui
        self.message_label.setText(label)
        self.message_text.setText(message)
        self.message_button.setText(button_label)

        self.stacked_widget.setCurrentIndex(0)

    def show_form(self, label: str, questions: dict, action: Callable) -> None:
        """
        вызов экрана заполнения формы вопросов
        :param label: главная надпись
        :param questions: вопросы в словаре, ключи - это вопрос, значения - ответы
            str - пустая строка
            int - число
            list - выбор значения из списка
        ":param action: функция вызываемая при отправке формы и принимающая аргумент словаря
        :return: пусто
        """
        assert isinstance(label, str), "Неверный тип 1 параметра метода"
        assert isinstance(questions, dict), "Неверный тип 2 параметра метода"
        for key, value in questions.items():
            assert isinstance(key, str), f"Неверный ключ >{key}< = {value} в словаре 2 параметра метода form_show()"
            assert isinstance(value, (str, int, list, EnumMeta)), f"Неверное значение {key} = >{value}< в словаря метода form_show()"
            if isinstance(value, list):
                for s in value:
                    assert isinstance(s, str), f"Неверный тип переменной в списке, должна быть строкой {key} = >{value}<"
        assert isinstance(action, Callable), "Неверный тип 4 параметра метода"

        # connect action
        self.disconnect_clicked_button(self.form_button)
        def event_action():
            answers = dict()
            for i, key in enumerate(questions.keys()):
                widget = self.form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget()
                answer = None
                if type(widget) == QLineEdit:
                    answer = widget.text()
                elif type(widget) == QComboBox:
                    answer = widget.currentText()
                elif type(widget) == QSpinBox:
                    answer = widget.value()
                answers.setdefault(key, answer)
            while self.form_layout.rowCount() > 0:
                self.form_layout.removeRow(0)
            action(answers)
        self.form_button.clicked.connect(event_action)

        # UI
        self.form_label.setText(label)
        for text, answer_type in questions.items():
            object_answer = None
            if type(answer_type) == str:
                object_answer = QLineEdit(text = answer_type)
            elif type(answer_type) == list:
                object_answer = QComboBox()
                for objs in answer_type:
                    object_answer.addItem(objs)
            elif type(answer_type) == int:
                object_answer = QSpinBox(value = answer_type)
            elif isinstance(answer_type, EnumMeta):
                object_answer = QComboBox()
                for enum in answer_type:
                    object_answer.addItem(str(enum.value))
            self.form_layout.addRow(text, object_answer)

        self.stacked_widget.setCurrentIndex(1)

    """МЕТОДЫ ДЛЯ РАБОТЫ С СЕССИЕЙ"""

    def begin_register(self):
        """
        method for begin registration new user
        create form data
        :return: None
        """
        # model predict by fice
        assert not self.student is None, "Объект student должен существовать"
        assert self.student.name == None, "Объект student должен иметь Name None"
        assert self.student.age == None, "Объект student должен иметь age None"
        assert self.student.is_male == None, "Объект student должен иметь is_male None"

        # AI predict
        is_male, age = True, 0
        if self.allow_camera:
            camera.snapshot("apps/PC/data/face_image_for_session.png")
            is_male, age = fast_insighface.analyze_face_male_age_by_file("apps/PC/data/face_image_for_session.png")

        # UI
        list_male = ["Мужчина", "Женщина"]
        if not is_male:
            list_male = list_male[::-1]
        self.show_form("Кто же вы?", {
            "Имя": "",
            "Возраст": age,
            "Пол": list_male
        }, self.end_register)

    def end_register(self, data: dict):
        """
        method for end registration new user
        read form data
        :return: None
        """
        assert not self.student is None, "Объект student должен существовать"
        assert self.student.name == None, "Объект student должен иметь Name None"
        assert self.student.age == None, "Объект student должен иметь age None"
        assert self.student.is_male == None, "Объект student должен иметь is_male None"
        assert isinstance(data, dict)

        # write data
        self.student.name = data["Имя"]
        self.student.age = data["Возраст"]
        self.student.is_male = data["Пол"] == "Мужской"

        # UI
        self.show_message(f"Добро пожаловать {self.student.name}", "", "Готово", self.begin_session)

    def begin_session(self):
        assert not self.student is None and self.session is None, "Состояние переменных не верно, возможно вы вызвали не подходящий метод begin_session()"

        self.session = Session(student_id = self.student.db_id)

        self.show_form("Как вы ?", {
            "Настроение": Mood,
            self.student.name: Self_Assessment
        }, self.continue_session)

    def continue_session(self, data: dict):
        assert not self.student is None and not self.session is None, "Состояние переменных не верно, возможно вы вызвали не подходящий метод continue_session()"
        assert self.session.mood is None and self.session.time is None and self.session.self_assessment is None, "Атрибуты сеанса при вызоре этого метода должны быть пусты"
        assert isinstance(data, dict), "Неверный аргумент data, возможно вы не использовали show_form()"

        game_launcher.modul_my_errors_run(1, self.snapshots, 3)

        self.session.mood = Mood(data["Настроение"])
        self.session.time = datetime.now()
        self.session.self_assessment = Self_Assessment(data[self.student.name])

        self.show_message("Хорош", "Молодец", "Выйти", self.close)

    """СЛУЖЕБНЫЕ МЕТОДЫ"""

    def disconnect_clicked_button(self, button: QPushButton):
        """Отключение всех action с кнопки"""
        try:
            button.clicked.disconnect()
        except TypeError:
            pass

if __name__ == "__main__":
    import sys
    import traceback
    def exception_hook(exc_type, exc_value, exc_tb):
        traceback.print_exception(exc_type, exc_value, exc_tb)
        sys.exit(1)
    sys.excepthook = exception_hook

    from py_model.student import Student
    app = QApplication(sys.argv)
    window = StudentWindow(Student(None, None, None))
    window.setFixedSize(800, 500)
    window.show()
    app.exit(app.exec())