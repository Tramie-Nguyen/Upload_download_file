from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QProgressBar, QStackedWidget, QLineEdit
from PyQt6.QtGui import QFont


class Loading_w(QMainWindow):
    def __init__(self):
        super(Loading_w, self).__init__()
        uic.loadUi("templates/loading_file.ui", self)

        # Initialize progress bar
        self.progressBar = self.findChild(QProgressBar, "progressBar")
        self.progressBar.setValue(0)

        # Initialize stacked widget for pictures
        self.pictureStack = self.findChild(QStackedWidget, "pictureStack")
        self.fileName2 = self.findChild(QLineEdit, "fileName2")

        font = QFont()
        font.setPointSize(14)
        self.fileName2.setFont(font)
        self.fileName2.setDisabled(True)
        self.work.setFont(font)
        self.work.setDisabled(True)

    def show_loading_picture(self):
        self.pictureStack.setCurrentIndex(0)

    def show_success_picture(self):
        self.pictureStack.setCurrentIndex(1)
