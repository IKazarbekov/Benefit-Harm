from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QApplication, QStackedLayout, \
    QStackedWidget, QFormLayout, QLineEdit, QSpinBox, QComboBox
import sys
import utils.camera as camera
from ml_model.face import fast_insighface
from py_model import student

class StudentWindow(QMainWindow):
    def __init__(self, student):
        super().__init__()
        self.student = student
        self.initUI()

        self.message_show("Benefit Harm", "Жду не дождусь", "Начать")

    def initUI(self):
        """
        initialization UI
        :return: None
        """
        """
        SCREEN TITLE
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

        # actions
        self.message_button.clicked.connect(self.begin_session)

        # boxes
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.message_label)
        vbox.addWidget(self.message_text)
        vbox.addWidget(self.message_button)

        """
        SCREEN FORM
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

        """
        CONTAINERS
        """
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

    def message_show(self, label: str, message: str, button_label: str) -> None:
        """
        For show one message
        :param label: big label
        :param message: small label
        :param button_label: text in button
        :return: None
        """
        self.stacked_widget.setCurrentIndex(0)
        self.message_label.setText(label)
        self.message_text.setText(message)
        self.message_button.setText(button_label)

    def begin_session(self):
        """
        method for begin registration new user
        create form data
        :return: None
        """
        # model predict by fice
        camera.snapshot("apps/PC/data/face_image_for_session.png")
        is_male, age = fast_insighface.analyze_face("apps/PC/data/face_image_for_session.png")

        # UI
        st = self.student
        cb_male = QComboBox()
        cb_male.addItem("Мужской")
        cb_male.addItem("Женский")
        self.form_label.setText("Заполните начальные данные")
        self.form_layout.addRow("Имя", QLineEdit())
        self.form_layout.addRow("Возраст", QSpinBox(value = age))
        self.form_layout.addRow("Пол", cb_male)
        self.form_button.clicked.connect(self.register)
        self.stacked_widget.setCurrentIndex(1)

    def register(self):
        """
        method for end registration new user
        read form data
        :return: None
        """
        student.name = self.form_layout.itemAt(0).widget().text()
        self.message_text.setText(f"Добро пожаловать {self.student.name}", "", "Готово")

if __name__ == "__main__":
    from py_model.student import Student
    app = QApplication(sys.argv)
    window = StudentWindow(Student(None, None, None))
    window.setFixedSize(800, 500)
    window.show()
    app.exit(app.exec())