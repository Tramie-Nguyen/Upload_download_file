from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QProgressBar, QLineEdit, QLabel, QStackedWidget
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

        self.work = self.findChild(QLabel, "work")
        self.fileName2 = self.findChild(QLineEdit, "fileName2")

        font = QFont()
        font.setPointSize(14)
        self.fileName2.setFont(font)
        self.fileName2.setDisabled(True)

        font2 = QFont()
        font2.setPointSize(18)
        font2.setBold(True)
        self.work.setFont(font2)

    def show_loading_picture(self):
        self.pictureStack.setCurrentIndex(0)
