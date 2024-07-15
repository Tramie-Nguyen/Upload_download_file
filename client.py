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
PORT = 4567
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024
SERVER_DATA_PATH = "Server_data"
CLIENT_DATA_PATH = "Client_data"
PATH = ""
CHECK = []
RECEIVE = []


print("CLIENT SIDE:")
client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_s.connect(ADDR)
except:
    print("ERROR! Can't connect to server side")
    client_s.close()
    sys.exit()


def handle_login():
    client_name = login_page.userName.text()
    client_pw = login_page.userPassword.text()
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


def get_unique_filename_in_server_data(file_name):
    base_name, extension = os.path.splitext(file_name)
    new_name = file_name
    count = 1

    while os.path.exists(os.path.join(SERVER_DATA_PATH, new_name)):
        new_name = f"{base_name}({count}){extension}"
        count += 1

    return new_name


def get_unique_filename_in_client_data(file_name):
    base_name, extension = os.path.splitext(file_name)
    new_name = file_name
    count = 1

    while os.path.exists(os.path.join(CLIENT_DATA_PATH, new_name)):
        new_name = f"{base_name}({count}){extension}"
        count += 1

    return new_name


def click_handler():
    dialog = QFileDialog()
    dialog.setNameFilter("All files (*)")
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    dialog_success = dialog.exec()

    if dialog_success == 1:
        selected_file_path = dialog.selectedFiles()[0]
        file_name = os.path.basename(selected_file_path)
        file_name_after_check = get_unique_filename_in_server_data(file_name)
        home_page2.fileName.setText(file_name_after_check)
        global PATH
        PATH = selected_file_path
        print("fileName:", file_name_after_check)
    else:
        print("User canceled selecting file")


def upload_file(file_path, file_name):
    send_file = f"Upload/{file_name}"
    client_s.send(send_file.encode(FORMAT))
    segments = divide_file_into_segments(file_path)
    # check if all segments have been sent or not
    while False in CHECK:
        create_segment_thread(segments)

    send_upload_full_segments = "Upload all segments successfully"
    print(send_upload_full_segments)
    client_s.sendall(send_upload_full_segments.encode(FORMAT))
    merge_result = client_s.recv(SIZE).decode(FORMAT)
    if merge_result == "SUCCESS":
        home_page2.append_file(file_name)
        home_page2.fileName.setText("")
        show_upload_success_w(file_name)
    else:
        show_upload_fail_w()
        home_page2.fileName.setText("")


def divide_file_into_segments(file_path):
    with open(file_path, "rb") as f:
        file_data = f.read()

    file_size = len(file_data)
    segments = [file_data[i : i + SIZE] for i in range(0, file_size, SIZE)]

    global CHECK
    CHECK = [0] * len(segments)
    client_s.sendall(f"{len(segments)}".encode(FORMAT))
    create_segment_thread(segments)
    return segments


def create_segment_thread(segments):
    threads = []

    for index, segment in enumerate(segments):
        if CHECK[index] == 1:
            continue
        else:
            t = threading.Thread(target=send_segment, args=(index, segment))
            threads.append(t)
            t.start()

    for t in threads:
        t.join()


def send_segment(segment_index, segment):
    client_s.sendall(f"{segment_index}".encode(FORMAT))
    client_s.sendall(segment)
    recv_msg = client_s.recv(SIZE).decode(FORMAT)
    key, index = recv_msg.split(" ")
    if key == "ack" and int(index) == segment_index:
        CHECK[segment_index] = 1
    time.sleep(0.1)


def download_file(file_name):
    if file_name == "":
        show_error_file_name_download()
    else:
        send_request = f"Download/{file_name}"
        client_s.sendall(send_request.encode(FORMAT))
        num_of_segments = client_s.recv(SIZE).decode(FORMAT)
        unique_file_name = get_unique_filename_in_client_data(file_name)
        if num_of_segments == "CAN'T FOUND":
            show_file_not_exist(file_name)
            home_page2.fileName.setText("")
            return
        else:
            num_of_segments = int(num_of_segments)
            global RECEIVE
            RECEIVE = [0] * num_of_segments
            segments = [None] * num_of_segments
            signal = 0
            # check if receive all segments or not
            while signal == 0:
                signal = recv_segment(segments)
            print("[RECEIVE ALL SEGMENTS]")

            merge_result = merge_segments_into_file(segments, unique_file_name)
            client_s.sendall(merge_result.encode(FORMAT))
            if merge_result == "SUCCESS":
                show_download_success(file_name)
                home_page2.append_downloaded_file(unique_file_name)
                home_page2.fileName.setText("")

            else:
                show_download_fail(file_name)
                home_page2.fileName.setText("")


def recv_segment(segments):
    segment_index = client_s.recv(SIZE).decode(FORMAT)
    if segment_index == "Download all segments successfully":
        print(segment_index)
        return 1
    segment_index = int(segment_index)
    if RECEIVE[segment_index] == 0:
        segments[segment_index] = client_s.recv(SIZE)
    else:
        ignore = client_s.recv(SIZE)
    client_s.sendall(f"ack {segment_index}".encode(FORMAT))
    RECEIVE[segment_index] = 1
    return 0


def merge_segments_into_file(segments, file_name):
    try:
        file_path = os.path.join(CLIENT_DATA_PATH, file_name)
        with open(file_path, "wb") as f:
            for segment in segments:
                f.write(segment)
        print("[MERGE SUCCESS] Merged segments into file successfully")
        return "SUCCESS"
    except Exception as e:
        print(f"[MERGE FAIL] Merging segments into file failed: {e}")
        return "FAIL"


def show_download_success(file_name):
    download_success = QMessageBox()
    download_success.setIcon(QMessageBox.Icon.Information)
    download_success.setText(f"Download file: {file_name} successfully")
    download_success.setWindowTitle("Download Success")
    download_success.exec()


def show_download_fail(file_name):
    download_fail = QMessageBox()
    download_fail.setIcon(QMessageBox.Icon.Warning)
    download_fail.setText(f"Fail to download file: {file_name}")
    download_fail.setWindowTitle("Download Error")
    download_fail.exec()


def show_error_file_name_download():
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Warning)
    error_dialog.setText("User forget to choose file to download")
    error_dialog.setWindowTitle("File error")
    error_dialog.exec()


def show_file_not_exist(file_name):
    f_not_exist = QMessageBox()
    f_not_exist.setIcon(QMessageBox.Icon.Warning)
    f_not_exist.setText(f"File {file_name} doesn't exist")
    f_not_exist.setWindowTitle("File error")
    f_not_exist.exec()


def show_upload_success_w(file_name):
    upload_success = QMessageBox()
    upload_success.setIcon(QMessageBox.Icon.Information)
    upload_success.setText(f"Upload file {file_name} successfully !!!")
    upload_success.setWindowTitle("Upload success")
    upload_success.exec()


def show_upload_fail_w():
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Warning)
    error_dialog.setText("UPLOAD FILE FAIL !!!")
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
