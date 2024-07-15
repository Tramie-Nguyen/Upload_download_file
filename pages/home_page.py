import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QListView, QScrollBar
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
