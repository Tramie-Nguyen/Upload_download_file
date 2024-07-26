from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QProgressBar


class Loading_w(QMainWindow):
    def __init__(self):
        super(Loading_w, self).__init__()
        uic.loadUi("templates/loading_page.ui", self)
        # Initialize progress bar
        self.progressBar = self.findChild(QProgressBar, "progressBar")
        self.progressBar.setValue(0)
