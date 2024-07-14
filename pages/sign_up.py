from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import pyqtSignal

from db import connect_database

ignore_message, User, file_col = connect_database()


class SignUp_w(QMainWindow):
    sign_up_success = pyqtSignal()

    def __init__(self):
        super(SignUp_w, self).__init__()
        uic.loadUi("templates/sign_up.ui", self)

    def show_error_name_window(self):
        error_name = QMessageBox()
        error_name.setIcon(QMessageBox.Icon.Warning)
        error_name.setText("ALREADY HAVE THIS NAME ")
        error_name.setWindowTitle("SignUp Error")
        error_name.exec()

    def show_success_window(self):
        success = QMessageBox()
        success.setIcon(QMessageBox.Icon.Information)
        success.setText("SIGN UP SUCCESSFULLY !!!")
        success.setWindowTitle("signUp success")
        success.exec()
