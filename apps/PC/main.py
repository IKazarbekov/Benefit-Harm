import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel

from student import StudentWindow
from py_model.student import Student


class StartWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Benefit Harm Launcher 0.0.1")
        self.setFixedSize(400, 200)

        self.initUI()

    def initUI(self):
        # widgets
        label = QLabel("Benefit Harm Launcher")
        button_student = QPushButton("Ученик", self)

        # styles
        label.setStyleSheet("font-size:20px;")
        button_student.setStyleSheet("font-size:20px;")

        # actions
        button_student.clicked.connect(self.new_user_action)

        # boxes
        central_widget = QWidget()
        vbox = QVBoxLayout(self)
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        # add in vbox
        vbox.addWidget(label)
        vbox.addWidget(button_student)

    def new_user_action(self):
        student = Student(None, None, None)
        self.window_student = StudentWindow(student)
        self.window_student.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.window_student.show()

# run
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    app.exit(app.exec())