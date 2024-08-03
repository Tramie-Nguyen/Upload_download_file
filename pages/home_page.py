import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QListView, QMessageBox, QFileDialog
from PyQt6.QtCore import QStringListModel, Qt
from PyQt6.QtGui import QFont
from db import connect_database

db_message, user_col, files_col = connect_database()
SERVER_DATA_PATH = "Server_data"


class HomePage_w(QMainWindow):

    def __init__(self):
        super(HomePage_w, self).__init__()
        uic.loadUi("templates/home_page.ui", self)
        self.fileName.setDisabled(True)
        font = QFont()
        font.setBold(True)
        font.setPointSize(25)
        self.label.setFont(font)

        font2 = QFont()
        font2.setPointSize(16)
        self.label_3.setFont(font2)
        self.label_5.setFont(font2)

        font3 = QFont()
        font3.setBold(True)
        font3.setPointSize(17)
        self.chooseFileButton.setFont(font3)
        self.uploadButton.setFont(font3)
        self.downloadButton.setFont(font3)

        # Initialize the QListView and QStringListModel for server files
        self.upload_list = self.findChild(QListView, "upload_list")
        self.model_upload = QStringListModel()
        self.upload_list.setModel(self.model_upload)
        self.upload_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        # Initialize the QListView and QStringListModel for client files
        self.download_list = self.findChild(QListView, "download_list")
        self.model_download = QStringListModel()
        self.download_list.setModel(self.model_download)
        self.download_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        # Connect buttons
        self.chooseFileButton.clicked.connect(self.choose_file_handler)

        # Connect the click event of the upload list to the handler
        self.upload_list.clicked.connect(self.handle_upload_list_click)
        self.clicked_file = False
        self.choose_file = False
        self.selected_file_name = ""
        self.selected_file_path = ""

    def get_user_name(self, user_name):
        self.load_initial_server_data_files(user_name)

    def load_initial_server_data_files(self, user_name):
        print(f"User name: {user_name}")
        user_file_names = self.get_user_files(user_name)
        self.model_upload.setStringList(user_file_names)

    def get_user_files(self, user_name):
        # Query the database for files with the owner matching the user_name
        query = {"owner": user_name}
        cursor = files_col.find(query)
        file_names = [file["file's name"] for file in cursor]
        return file_names

    def choose_file_handler(self):
        self.selected_file_name = ""
        dialog = QFileDialog()
        dialog.setNameFilter("All files (*)")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog_success = dialog.exec()

        if dialog_success == 1:
            self.selected_file_path = dialog.selectedFiles()[0]
            file_name = os.path.basename(self.selected_file_path)
            self.fileName.setText(file_name)
            print("fileName:", file_name)
            self.choose_file = True
            self.clicked_file = False
            self.fileName.setDisabled(False)

        else:
            print("User canceled selecting file")
            self.choose_file = False

    def handle_upload_list_click(self, index):
        file_name = self.model_upload.data(index, Qt.ItemDataRole.DisplayRole)
        self.fileName.setText(file_name)
        print(f"Selected file from upload list: {file_name}")
        self.selected_file_name = file_name
        self.clicked_file = True
        self.choose_file = False

    def append_file(self, file_name, owner):
        current_files = self.model_upload.stringList()
        current_files.append(file_name)
        self.model_upload.setStringList(current_files)

        # Insert a new document into the files collection in the database
        file_document = {"file's name": file_name, "owner": owner}
        files_col.insert_one(file_document)

    def append_downloaded_file(self, file_name):
        current_downloaded_files = self.model_download.stringList()
        current_downloaded_files.append(file_name)
        self.model_download.setStringList(current_downloaded_files)

    def show_download_fail(self, file_name):
        download_fail = QMessageBox()
        download_fail.setIcon(QMessageBox.Icon.Critical)
        download_fail.setText(f"Fail to download file: {file_name}")
        download_fail.setWindowTitle("Download Error")
        download_fail.exec()

    def show_error_choose_file_to_download(self):
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

    def show_error_file_name(self):
        error_f_name = QMessageBox()
        error_f_name.setIcon(QMessageBox.Icon.Warning)
        error_f_name.setText(f"Invalid file's name")
        error_f_name.setWindowTitle("Invalid file's name")
        error_f_name.exec()

    def show_upload_fail_w(self, file_name):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(f"Upload file {file_name} fail !!!")
        error_dialog.setWindowTitle("Upload Error")
        error_dialog.exec()

    def procedure_error(self):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("Invalid request ")
        error_dialog.setWindowTitle("Procedure error")
        error_dialog.exec()
