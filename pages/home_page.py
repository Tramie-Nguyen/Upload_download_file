import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QListView, QMessageBox
from PyQt6.QtCore import QStringListModel, Qt
from db import connect_database


FORMAT = "utf-8"
SIZE = 1024
SERVER_DATA_PATH = "Server_data"
CLIENT_DOWNLOAD_PATH = "Client_data"
db_message, user_col, file_col = connect_database()


class HomePage_w(QMainWindow):

    def __init__(self):
        super(HomePage_w, self).__init__()
        uic.loadUi("templates/home_page.ui", self)
        self.upload_list = self.findChild(QListView, "upload_list")
        self.download_list = self.findChild(QListView, "download_list")
        self.model_upload = QStringListModel()
        self.model_download = QStringListModel()
        self.upload_list.setModel(self.model_upload)
        self.download_list.setModel(self.model_download)
        self.read_and_show_file_info()
        self.load_initial_client_data_files()
        self.load_initial_server_data_files()

    def read_and_show_file_info(self):
        files_info = file_col.find({}, {"file_name": 1, "owner": 1, "_id": 0})
        files_list = [
            f"{file['file_name']} (Owner: {file['owner']})" for file in files_info
        ]
        self.model_upload.setStringList(files_list)

    def load_initial_server_data_files(self):
        files = os.listdir(SERVER_DATA_PATH)
        self.model_upload.setStringList(files)

    def load_initial_client_data_files(self):
        files = os.listdir(CLIENT_DOWNLOAD_PATH)
        self.model_download.setStringList(files)

    def append_file(self, file_name, owner):
        current_files = self.model_upload.stringList()
        current_files.append(f"{file_name} (Owner: {owner})")
        self.model_upload.setStringList(current_files)
        file_col.insert_one({"file_name": file_name, "owner": owner})

    def append_downloaded_file(self, file_name):
        current_downloaded_files = self.model_download.stringList()
        current_downloaded_files.append(file_name)
        self.model_download.setStringList(current_downloaded_files)
