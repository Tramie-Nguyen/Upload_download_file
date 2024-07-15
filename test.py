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

        # Initialize the QListView and QStringListModel
        self.upload_list = self.findChild(QListView, "upload_list")
        self.model = QStringListModel()
        self.upload_list.setModel(self.model)

        # Load initial server data
        self.load_initial_server_data()

    def load_initial_server_data(self):
        file_names = self.get_file_names()
        self.model.setStringList(file_names)

    def get_file_names(self):
        file_names = []
        for file_name in os.listdir(SERVER_DATA_PATH):
            if os.path.isfile(os.path.join(SERVER_DATA_PATH, file_name)):
                file_names.append(file_name)
        return file_names

    def handle_item_clicked(self, index):
        # Get the clicked file name
        file_name = self.model.data(index, Qt.ItemDataRole.DisplayRole)

        # Show a message box for demonstration purposes
        QMessageBox.information(self, "Download", f"Selected file: {file_name}")

        # Implement the download logic here
        # self.download_file(file_name)

    def download_file(self, file_name):
        # Implement your file download logic here
        pass


# Connect to the database
def connect_database():
    # Implement your database connection logic here
    pass
