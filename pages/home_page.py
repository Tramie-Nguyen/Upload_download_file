import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QListView, QMessageBox
from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtGui import QFont


FORMAT = "utf-8"
SIZE = 1024
SERVER_DATA_PATH = "Server_data"
CLIENT_DATA_PATH = "Client_data"


class HomePage_w(QMainWindow):

    def __init__(self):
        super(HomePage_w, self).__init__()
        uic.loadUi("templates/home_page.ui", self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(25)
        self.label.setFont(font)

        font2 = QFont()
        font2.setPointSize(14)
        self.label_3.setFont(font2)
        self.label_5.setFont(font2)

        font3 = QFont()
        font3.setBold(True)
        font3.setPointSize(14)
        self.chooseFileButton.setFont(font3)
        self.uploadButton.setFont(font3)
        self.downloadButton.setFont(font3)

        # Initialize the QListView and QStringListModel for server files
        self.upload_list = self.findChild(QListView, "upload_list")
        self.model_upload = QStringListModel()
        self.upload_list.setModel(self.model_upload)
        self.load_initial_server_data_files()

        self.upload_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        self.load_initial_server_data_files()

        # Initialize the QListView and QStringListModel for client files
        self.download_list = self.findChild(QListView, "download_list")
        self.model_download = QStringListModel()
        self.download_list.setModel(self.model_download)
        self.load_initial_client_data_files()
        self.download_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.load_initial_client_data_files()

        # Connect the click event of the upload list to the handler
        self.upload_list.clicked.connect(self.handle_upload_list_click)

    def load_initial_server_data_files(self):
        server_file_names = self.get_file_names(SERVER_DATA_PATH)
        self.model_upload.setStringList(server_file_names)

    def load_initial_client_data_files(self):
        client_file_names = self.get_file_names(CLIENT_DATA_PATH)
        self.model_download.setStringList(client_file_names)

    def get_file_names(self, folder_path):
        file_names = []
        for file_name in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, file_name)):
                file_names.append(file_name)
        return file_names

    def handle_upload_list_click(self, index):
        file_name = self.model_upload.data(index, Qt.ItemDataRole.DisplayRole)
        self.fileName.setText(file_name)
        print(f"Selected file from upload list: {file_name}")

    def handle_download_list_click(self, index):
        file_name = self.model_download.data(index, Qt.ItemDataRole.DisplayRole)
        self.fileName.setText(file_name)
        print(f"Selected file from download list: {file_name}")

    def append_file(self, file_name):
        current_files = self.model_upload.stringList()
        current_files.append(file_name)
        self.model_upload.setStringList(current_files)

    def append_downloaded_file(self, file_name):
        current_downloaded_files = self.model_download.stringList()
        current_downloaded_files.append(file_name)
        self.model_download.setStringList(current_downloaded_files)

    def show_download_success(self, file_name):
        download_success = QMessageBox()
        download_success.setIcon(QMessageBox.Icon.Information)
        download_success.setText(f"Download file: {file_name} successfully")
        download_success.setWindowTitle("Download Success")
        download_success.exec()

    def show_download_fail(self, file_name):
        download_fail = QMessageBox()
        download_fail.setIcon(QMessageBox.Icon.Critical)
        download_fail.setText(f"Fail to download file: {file_name}")
        download_fail.setWindowTitle("Download Error")
        download_fail.exec()

    def show_error_file_name_download(self):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Warning)
        error_dialog.setText("User forget to choose file to download")
        error_dialog.setWindowTitle("File error")
        error_dialog.exec()

    def file_name_not_exist(self, file_name):
        f_not_exist = QMessageBox()
        f_not_exist.setIcon(QMessageBox.Icon.Warning)
        f_not_exist.setText(f"File {file_name} doesn't exist")
        f_not_exist.setWindowTitle("File error")
        f_not_exist.exec()

    def show_error_choose_file(self):
        error_choose_f = QMessageBox()
        error_choose_f.setIcon(QMessageBox.Icon.Warning)
        error_choose_f.setText(f"User has not selected a file to upload")
        error_choose_f.setWindowTitle("Choose file error")
        error_choose_f.exec()

    def show_error_file_name_upload(self):
        error_f_name = QMessageBox()
        error_f_name.setIcon(QMessageBox.Icon.Warning)
        error_f_name.setText(f"Invalid file's name")
        error_f_name.setWindowTitle("Invalid file's name")
        error_f_name.exec()

    def show_upload_success_w(self, file_name):
        upload_success = QMessageBox()
        upload_success.setIcon(QMessageBox.Icon.Information)
        upload_success.setText(f"Upload file {file_name} successfully !!!")
        upload_success.setWindowTitle("Upload success")
        upload_success.exec()

    def show_upload_fail_w(self, file_name):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(f"Upload file {file_name} fail !!!")
        error_dialog.setWindowTitle("Upload Error")
        error_dialog.exec()
