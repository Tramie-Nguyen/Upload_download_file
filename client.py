import os
import socket
import threading
import time
import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QFileDialog
from pages import login, sign_up, home_page, loading_page
from dotenv import load_dotenv

load_dotenv()
client_lock = threading.Lock()

IP = "127.0.0.1"
PORT = 45999
ADDR = (IP, PORT)
FORMAT = "utf-8"
SIZE = 1024


def connect_to_server(max_retries=5):
    print("CLIENT SIDE:")
    client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    attempt = 0

    while attempt < max_retries:
        try:
            client_s.connect(ADDR)
            print("Connected to server successfully.")
            return client_s
        except Exception as e:
            print(f"ERROR! Can't connect to server: {e}")
            attempt += 1

            time.sleep(0.5)

    print("Max retries reached. Exiting.")
    client_s.close()
    sys.exit()


client_s = connect_to_server()


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


def download_click_handler():
    origin_file_name = home_page2.selected_file_name
    client_file_path, _ = QFileDialog.getSaveFileName(
        None, "Save File", origin_file_name, "All Files (*)"
    )
    if client_file_path:
        client_data_path = os.path.dirname(client_file_path)
        base_name = os.path.basename(client_file_path)

        print(f"User choose to store in :{client_data_path}")
        print(f"file name after rename: {base_name}")
        download_file(base_name, client_data_path)
    else:
        print("user canceled choose place to store download file")


def upload_file(file_path, file_name):
    # chon file trong list upload -> co path
    if home_page2.clicked_file == True:
        home_page2.procedure_error()
        home_page2.fileName.setText("")
        return

    elif not file_name.strip() and file_path == "":  # chua chon file, ten file rong
        home_page2.show_error_choose_file()
        home_page2.fileName.setText("")
        return

    elif file_path == "":  # chua chon file, user nhap ten bua
        home_page2.file_name_not_exist(file_name)
        home_page2.fileName.setText("")
        return

    elif not file_name.strip() and file_path != "":  # chon file nhung ten rong
        home_page2.show_error_file_name()
        home_page2.fileName.setText("")
        return

    elif "." not in file_name:  # file ko co duoi
        extension = file_path.split(".")[-1]
        file_name += "."
        file_name += extension

    send_file = f"Upload/{file_name}"
    client_s.sendall(send_file.encode(FORMAT))
    unique_name = client_s.recv(SIZE).decode(FORMAT)
    segments = divide_file_into_segments(file_path)

    # show loading_page
    stack_widget.setCurrentIndex(3)
    loading_page2.show_loading_picture()
    loading_page2.progressBar.setValue(0)
    loading_page2.progressBar.setMaximum(len(segments))
    loading_page2.fileName2.setText(unique_name)
    loading_page2.work.setText("Uploading file...")

    create_segment_thread(segments)

    send_upload_full_segments = "Upload all segments successfully"
    print(send_upload_full_segments)

    merge_result = client_s.recv(SIZE).decode(FORMAT)

    if merge_result == "SUCCESS":
        home_page2.append_file(unique_name)
        loading_page2.show_success_picture()  # Show end picture
        time.sleep(2)
        stack_widget.setCurrentIndex(2)

    else:
        stack_widget.setCurrentIndex(2)
        home_page2.show_upload_fail_w(file_name)

    home_page2.selected_file_path = ""
    home_page2.fileName.setText("")
    home_page2.choose_file = False
    stack_widget.setCurrentIndex(2)


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
        try:
            with client_lock:
                client_s.sendall(f"{segment_index}".encode(FORMAT))
                client_s.recv(SIZE)
                client_s.sendall(segment)
                recv_msg = client_s.recv(SIZE).decode(FORMAT)
                key, index = recv_msg.split(" ")
                if key == "ack" and int(index) == segment_index:
                    print(f"ack {segment_index}")
                    # Update progress bar
                    loading_page2.progressBar.setValue(segment_index + 1)
                    break
                else:
                    print(f"nak {segment_index}")
                    time.sleep(0.5)
                    continue
        except:
            print(f"Error sending segment {segment_index}: Retrying...")


def download_file(file_name, client_path):
    if home_page2.clicked_file == False:  # chua chon file
        home_page2.show_error_choose_file_to_download()
        return
    elif not home_page2.fileName.text().strip():  # chon r nhung dat ten ko hop le
        home_page2.show_error_file_name()
        return

    send_file = f"Download/{home_page2.selected_file_name}"  # ten file trong server_data ma user chon
    client_s.sendall(send_file.encode(FORMAT))
    client_s.recv(SIZE)
    client_s.sendall(f"{file_name}@{client_path}".encode(FORMAT))  # file rename
    server_msg = client_s.recv(SIZE).decode(FORMAT)

    if server_msg == "CAN'T FOUND":
        home_page2.file_name_not_exist(home_page2.selected_file_name)
        return

    unique_name = server_msg
    print(unique_name)
    client_s.sendall(unique_name.encode(FORMAT))

    num_of_segments = int(client_s.recv(SIZE).decode(FORMAT))
    segments = [None] * num_of_segments

    # show loading_page
    stack_widget.setCurrentIndex(3)
    loading_page2.show_loading_picture()
    loading_page2.progressBar.setValue(0)
    loading_page2.progressBar.setMaximum(len(segments))
    loading_page2.fileName2.setText(unique_name)
    loading_page2.work.setText("Downloading file...")

    signal = 0
    while signal == 0:
        with client_lock:
            signal = recv_segment(num_of_segments, segments)

    print("[RECEIVE ALL SEGMENTS]")
    merge_result = merge_segments_into_file(segments, unique_name, client_path)

    if merge_result == "SUCCESS":
        loading_page2.show_success_picture()
        home_page2.append_downloaded_file(unique_name)
        home_page2.fileName.setText("")
        time.sleep(2)
        stack_widget.setCurrentIndex(2)

    else:
        stack_widget.setCurrentIndex(2)
        home_page2.show_download_fail(file_name)
        home_page2.fileName.setText("")

    home_page2.clicked_file = False
    home_page2.selected_file_name = ""


def recv_segment(num_of_segments, segments):
    for _ in range(num_of_segments):
        while True:
            try:
                segment_index = int(client_s.recv(SIZE).decode(FORMAT))
                client_s.sendall("ok".encode(FORMAT))
                segment = client_s.recv(SIZE)
                segments[segment_index] = segment
                client_s.sendall(f"ack {segment_index}".encode(FORMAT))
                # Update progress bar
                loading_page2.progressBar.setValue(segment_index + 1)
                break

            except:
                client_s.sendall(f"nak {segment_index}".encode(FORMAT))
                print(f"Error receiving segment {segment_index}: Retrying...")
    return 1


def merge_segments_into_file(segments, file_name, client_path):
    try:
        file_path = os.path.join(client_path, file_name)
        with open(file_path, "wb") as f:
            for segment in segments:
                f.write(segment)
        print("[MERGE SUCCESS] merge segments into file successfully")
        return "SUCCESS"
    except:
        print("[MERGE FAIL] merge segments into file fail")
        return "FAIL"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_page = login.Login_w()
    signup_page = sign_up.SignUp_w()
    home_page2 = home_page.HomePage_w()
    loading_page2 = loading_page.Loading_w()

    # Allow multiple windows to be managed
    stack_widget = QStackedWidget()
    stack_widget.addWidget(login_page)
    stack_widget.addWidget(signup_page)
    stack_widget.addWidget(home_page2)
    stack_widget.addWidget(loading_page2)

    # Handle switch page
    login_page.loginButton.clicked.connect(handle_login)
    login_page.signUpButton.clicked.connect(lambda: stack_widget.setCurrentIndex(1))
    login_page.login_successful.connect(lambda: stack_widget.setCurrentIndex(2))
    signup_page.signUpButton.clicked.connect(handle_sign_up)
    signup_page.loginButton.clicked.connect(lambda: stack_widget.setCurrentIndex(0))
    signup_page.sign_up_success.connect(lambda: stack_widget.setCurrentIndex(0))
    home_page2.uploadButton.clicked.connect(
        lambda: upload_file(home_page2.selected_file_path, home_page2.fileName.text())
    )
    home_page2.downloadButton.clicked.connect(download_click_handler)

    stack_widget.setCurrentIndex(0)
    stack_widget.setFixedHeight(600)
    stack_widget.setFixedWidth(850)
    stack_widget.show()

    sys.exit(app.exec())
