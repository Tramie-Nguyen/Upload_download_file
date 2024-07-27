from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class SignUp_w(QMainWindow):
    sign_up_success = pyqtSignal()

    def __init__(self):
        super(SignUp_w, self).__init__()
        uic.loadUi("templates/sign_up.ui", self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(25)
        self.label.setFont(font)

        font2 = QFont()
        font2.setBold(True)
        font2.setPointSize(15)
        self.label_2.setFont(font2)
        self.label_3.setFont(font2)

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

    def show_error_sign_up(self):
        error_signup = QMessageBox()
        error_signup.setIcon(QMessageBox.Icon.Warning)
        error_signup.setText("Sign up fail ! \n Invalid account")
        error_signup.setWindowTitle("SignUp Error")
        error_signup.exec()
