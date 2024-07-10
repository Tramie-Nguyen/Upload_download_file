from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox

from db import connect_database

ignore_message, User, file_col = connect_database()


class SignUp_w(QMainWindow):

    def __init__(self):
        super(SignUp_w, self).__init__()
        uic.loadUi("templates/sign_up.ui", self)
        self.signUpButton.clicked.connect(self.handle_sign_up)

    def handle_sign_up(self):
        name = self.newUserName.text()
        pw = self.newUserPassword.text()
        if User.find_one({"name": name}):
            self.show_error_name_window()

        else:
            data = {"name": name, "password": pw}
            User.insert_one(data)
            self.show_success_window()

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
