from PyQt6 import uic
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont


class Login_w(QMainWindow):
    login_successful = pyqtSignal()

    def __init__(self):
        super(Login_w, self).__init__()
        uic.loadUi("templates/login.ui", self)

        font = QFont()
        font.setBold(True)
        font.setPointSize(25)
        self.label.setFont(font)

        font2 = QFont()
        font2.setBold(True)
        font2.setPointSize(13)
        self.label_2.setFont(font2)
        self.label_3.setFont(font2)

    def show_error_login_window(self):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.setText("LOGIN FAIL !!! \n ACCOUNT DOESN'T EXIST")
        error_dialog.setWindowTitle("Login Error")
        error_dialog.exec()

    def show_success_login_window(self):
        success_dialog = QMessageBox()
        success_dialog.setIcon(QMessageBox.Icon.Information)
        success_dialog.setText("LOGIN SUCCESS !!!")
        success_dialog.setWindowTitle("Notification")
        success_dialog.exec()

    def show_wrong_password_window(self):
        wrong_pw = QMessageBox()
        wrong_pw.setIcon(QMessageBox.Icon.Warning)
        wrong_pw.setText("WRONG PASSWORD !!!")
        wrong_pw.setWindowTitle("wrong password")
        wrong_pw.exec()
