import os
import socket
import threading
import time
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QFileDialog, QMessageBox
from pages import login, sign_up, home_page
from dotenv import load_dotenv

load_dotenv()

IP = "127.0.0.1"
PORT = 45999
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
PATH = ""
ACK_MSG = "ACK"
NAK_MSG = "NAK"

print("CLIENT SIDE:")
client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_s.connect(ADDR)
except Exception as e:
    print(f"ERROR! Can't connect to server: {e}")
    client_s.close()
    sys.exit()


def handle_login():
    client_name = login_page.userName.text()
    client_pw = login_page.userPassword.text()
    check_name = client_name.strip()
    check_pw = client_pw.strip()

    if not check_name or not check_pw:
        login_page.show_empty_name_or_password()
        login_page.userPassword.setText("")
        login_page.userName.setText("")
        return
    client_data = f"Login/{client_name}/{client_pw}"
    client_s.sendall(client_data.encode(FORMAT))
    login_result = client_s.recv(SIZE).decode(FORMAT)

    if login_result == "Login success":
        login_page.show_success_login_window()
        login_page.login_successful.emit()

    elif login_result == "Wrong password":
        login_page.userPassword.setText("")
        login_page.userName.setText("")
        login_page.show_wrong_password_window()
    else:
        login_page.userPassword.setText("")
        login_page.userName.setText("")
        login_page.show_error_login_window()


def handle_sign_up():
    client_new_name = signup_page.newUserName.text()
    client_new_pw = signup_page.newUserPassword.text()
    check_new_name = client_new_name.strip()
    check_new_pw = client_new_pw.strip()
    if not check_new_name or not check_new_pw:
        signup_page.show_error_sign_up()
        signup_page.newUserName.setText("")
        signup_page.newUserPassword.setText("")
        return
    client_data = f"SignUp/{client_new_name}/{client_new_pw}"
    client_s.sendall(client_data.encode(FORMAT))
    sign_up_result = client_s.recv(SIZE).decode(FORMAT)

    if sign_up_result == "Already has this name":
        signup_page.show_error_name_window()
        signup_page.newUserName.setText("")
        signup_page.newUserPassword.setText("")
    else:
        signup_page.show_success_window()
        signup_page.newUserName.setText("")
        signup_page.newUserPassword.setText("")
        signup_page.sign_up_success.emit()


def click_handler():
    dialog = QFileDialog()
    dialog.setNameFilter("All files (*)")
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    dialog_success = dialog.exec()

    if dialog_success == 1:
        selected_file_path = dialog.selectedFiles()[0]
        file_name = os.path.basename(selected_file_path)
        global PATH
        PATH = selected_file_path
        home_page2.fileName.setText(file_name)
        print("fileName:", file_name)
    else:
        print("User canceled selecting file")


def upload_file(file_path, file_name):
    if (not file_name.strip() or file_name == "") and file_path == "":
        show_error_choose_file()
        home_page2.fileName.setText("")
        return
    elif (not file_name.strip() or file_name == "") and file_path != "":
        show_error_file_name_upload()
        home_page2.fileName.setText("")
        return

    send_file = f"Upload/{file_name}"
    client_s.send(send_file.encode(FORMAT))
    segments = divide_file_into_segments(file_path)
    create_segment_thread(segments)

    send_upload_full_segments = "Upload all segments successfully"
    print(send_upload_full_segments)

    merge_result = client_s.recv(SIZE).decode(FORMAT)
    unique_name = client_s.recv(SIZE).decode(FORMAT)
    if merge_result == "SUCCESS":
        home_page2.append_file(unique_name)
        home_page2.fileName.setText("")
        show_upload_success_w(unique_name)
    else:
        show_upload_fail_w(file_name)
        home_page2.fileName.setText("")


def divide_file_into_segments(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()
    file_size = len(file_data)
    segments = [file_data[i : i + SIZE] for i in range(0, file_size, SIZE)]
    client_s.sendall(f"{len(segments)}".encode(FORMAT))
    return segments


def create_segment_thread(segments):
    threads = []
    for index, segment in enumerate(segments):
        t = threading.Thread(target=send_segment, args=(index, segment))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def send_segment(segment_index, segment):
    while True:
        client_s.sendall(f"{segment_index}".encode(FORMAT))
        client_s.sendall(segment)
        recv_msg = client_s.recv(SIZE).decode(FORMAT)
        key, index = recv_msg.split(" ")
        if key == "ack" and int(index) == segment_index:
            print(f"ack {segment_index}")
            break
        else:
            print(f"nak {segment_index}")
            time.sleep(0.5)
            continue


def download_file(file_name):
    pass


def show_download_success(file_name):
    download_success = QMessageBox()
    download_success.setIcon(QMessageBox.Icon.Information)
    download_success.setText(f"Download file: {file_name} successfully")
    download_success.setWindowTitle("Download Success")
    download_success.exec()


def show_download_fail(file_name):
    download_fail = QMessageBox()
    download_fail.setIcon(QMessageBox.Icon.Critical)
    download_fail.setText(f"Fail to download file: {file_name}")
    download_fail.setWindowTitle("Download Error")
    download_fail.exec()


def show_error_file_name_download():
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Warning)
    error_dialog.setText("User forget to choose file to download")
    error_dialog.setWindowTitle("File error")
    error_dialog.exec()


def show_error_choose_file():
    error_choose_f = QMessageBox()
    error_choose_f.setIcon(QMessageBox.Icon.Warning)
    error_choose_f.setText(f"User has not selected a file to upload")
    error_choose_f.setWindowTitle("Choose file error")
    error_choose_f.exec()


def show_error_file_name_upload():
    error_f_name = QMessageBox()
    error_f_name.setIcon(QMessageBox.Icon.Warning)
    error_f_name.setText(f"Invalid file's name")
    error_f_name.setWindowTitle("Invalid file's name")
    error_f_name.exec()


def show_upload_success_w(file_name):
    upload_success = QMessageBox()
    upload_success.setIcon(QMessageBox.Icon.Information)
    upload_success.setText(f"Upload file {file_name} successfully !!!")
    upload_success.setWindowTitle("Upload success")
    upload_success.exec()


def show_upload_fail_w(file_name):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setText(f"Upload file {file_name} fail !!!")
    error_dialog.setWindowTitle("Upload Error")
    error_dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_page = login.Login_w()
    signup_page = sign_up.SignUp_w()
    home_page2 = home_page.HomePage_w()

    # Allow multiple windows to be managed
    stack_widget = QStackedWidget()
    stack_widget.addWidget(login_page)
    stack_widget.addWidget(signup_page)
    stack_widget.addWidget(home_page2)

    # Handle switch page
    login_page.loginButton.clicked.connect(handle_login)
    login_page.signUpButton.clicked.connect(lambda: stack_widget.setCurrentIndex(1))
    login_page.login_successful.connect(lambda: stack_widget.setCurrentIndex(2))
    signup_page.signUpButton.clicked.connect(handle_sign_up)
    signup_page.loginButton.clicked.connect(lambda: stack_widget.setCurrentIndex(0))
    signup_page.sign_up_success.connect(lambda: stack_widget.setCurrentIndex(0))
    home_page2.chooseFileButton.clicked.connect(click_handler)
    home_page2.uploadButton.clicked.connect(
        lambda: upload_file(PATH, home_page2.fileName.text())
    )
    home_page2.downloadButton.clicked.connect(
        lambda: download_file(home_page2.fileName.text())
    )

    stack_widget.setCurrentIndex(0)
    stack_widget.setFixedHeight(600)
    stack_widget.setFixedWidth(850)
    stack_widget.show()

    sys.exit(app.exec())
