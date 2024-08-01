import os
import io
import docx
from PyQt5.QtWidgets import (QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QHBoxLayout,
                             QListWidget, QTextEdit, QLabel, QDateEdit, QFileDialog, QWidget, QMainWindow, QTabWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyPDF2 import PdfReader
import logging

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        layout = QFormLayout(self)
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)

        login_button = QPushButton("Login", self)
        login_button.clicked.connect(self.accept)
        layout.addRow(login_button)

        register_button = QPushButton("Register", self)
        register_button.clicked.connect(self.register)
        layout.addRow(register_button)

    def register(self):
        self.parent().show_registration_dialog()
        self.close()

class RegistrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register")
        self.setModal(True)

        layout = QFormLayout(self)
        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)

        register_button = QPushButton("Register", self)
        register_button.clicked.connect(self.accept)
        layout.addRow(register_button)

class ResumeViewWindow(QMainWindow):
    def __init__(self, text, filename, file_type):
        super().__init__()
        self.setWindowTitle(f"Resume: {filename}")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(text)
        layout.addWidget(text_edit)

class ResumeManagementTab(QWidget):
    resume_selected = pyqtSignal(str, str)
    cover_letter_requested = pyqtSignal(str, str)

    def __init__(self, user_id, database, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.db = database
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        upload_btn = QPushButton("Upload Resume")
        upload_btn.clicked.connect(self.upload_resume)
        left_layout.addWidget(upload_btn)

        self.resume_list = QListWidget()
        self.resume_list.itemClicked.connect(self.view_resume)
        left_layout.addWidget(self.resume_list)

        delete_btn = QPushButton("Delete Selected Resume")
        delete_btn.clicked.connect(self.delete_resume)
        left_layout.addWidget(delete_btn)

        create_cover_letter_btn = QPushButton("Create Cover Letter")
        create_cover_letter_btn.clicked.connect(self.request_cover_letter)
        left_layout.addWidget(create_cover_letter_btn)

        self.resume_view = QTextEdit()
        self.resume_view.setReadOnly(True)
        right_layout.addWidget(QLabel("Resume Content:"))
        right_layout.addWidget(self.resume_view)

        self.application_view = QTextEdit()
        self.application_view.setReadOnly(True)
        right_layout.addWidget(QLabel("Job Application:"))
        right_layout.addWidget(self.application_view)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.setLayout(layout)
        self.load_resumes()

    def upload_resume(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Upload Resume", "", "PDF Files (*.pdf);;Word Files (*.docx)")
        if file_path:
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as file:
                content = file.read()
            self.db.add_resume(self.user_id, file_name, content)
            self.load_resumes()

    def load_resumes(self):
        self.resume_list.clear()
        resumes = self.db.get_resumes(self.user_id)
        for resume in resumes:
            self.resume_list.addItem(resume[2])  # Assuming filename is at index 2

    def view_resume(self, item):
        try:
            resume = self.db.get_resume_by_filename(self.user_id, item.text())
            if resume:
                content = resume[3]  # Assuming content is at index 3
                filename = resume[2]  # Assuming filename is at index 2
                file_type = 'pdf' if filename.lower().endswith('.pdf') else 'docx' if filename.lower().endswith('.docx') else 'txt'

                # Decode the content based on the file type
                if file_type == 'pdf':
                    content = self.read_pdf(content)
                elif file_type == 'docx':
                    content = self.read_docx(content)
                else:
                    content = content.decode('utf-8')  # Assuming plain text content is utf-8 encoded

                self.resume_selected.emit(str(self.user_id), filename)
                resume_view_window = ResumeViewWindow(content, filename, file_type)
                resume_view_window.show()

                # Keep a reference to the window to prevent it from being garbage collected
                self.resume_view_window = resume_view_window
            else:
                QMessageBox.warning(self, "Resume Not Found", "The selected resume could not be found.")
        except Exception as e:
            logging.error(f"Error viewing resume: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while viewing the resume: {str(e)}")

    def delete_resume(self):
        current_item = self.resume_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "Delete Resume",
                                         f"Are you sure you want to delete {current_item.text()}?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.delete_resume(self.user_id, current_item.text())
                self.load_resumes()

    def request_cover_letter(self):
        current_item = self.resume_list.currentItem()
        if current_item:
            self.cover_letter_requested.emit(str(self.user_id), current_item.text())
            QMessageBox.information(self, "Cover Letter", "Cover letter creation in progress.")

    def read_pdf(self, content):
        pdf_reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() for page in pdf_reader.pages)

    def read_docx(self, content):
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)

class AddApplicationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Application")
        self.setModal(True)

        layout = QFormLayout(self)
        self.company_input = QLineEdit(self)
        self.position_input = QLineEdit(self)
        self.job_description_input = QTextEdit(self)
        self.contact_person_input = QLineEdit(self)
        self.date_input = QDateEdit(self)
        self.date_input.setDate(QDate.currentDate())

        layout.addRow("Company:", self.company_input)
        layout.addRow("Position:", self.position_input)
        layout.addRow("Job Description:", self.job_description_input)
        layout.addRow("Contact Person:", self.contact_person_input)
        layout.addRow("Date:", self.date_input)

        add_button = QPushButton("Add Application", self)
        add_button.clicked.connect(self.accept)
        layout.addRow(add_button)

class ApplicationTrackingTab(QWidget):
    application_selected = pyqtSignal(str, str, str)  # Signal for application selection (user_id, company, position)

    def __init__(self, user_id, database):
        super().__init__()
        self.user_id = user_id
        self.db = database
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        add_btn = QPushButton("Add Application")
        add_btn.clicked.connect(self.add_application)
        layout.addWidget(add_btn)

        self.application_list = QListWidget()
        self.application_list.itemDoubleClicked.connect(self.view_application)
        layout.addWidget(self.application_list)

        delete_btn = QPushButton("Delete Selected Application")
        delete_btn.clicked.connect(self.delete_application)
        layout.addWidget(delete_btn)

        self.setLayout(layout)
        self.load_applications()

    def add_application(self):
        dialog = AddApplicationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                company = dialog.company_input.text()
                position = dialog.position_input.text()
                job_description = dialog.job_description_input.toPlainText()
                contact_person = dialog.contact_person_input.text()
                date = dialog.date_input.date().toString("yyyy-MM-dd")

                self.db.add_application(self.user_id, company, position, job_description, contact_person, date)
                self.load_applications()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while adding the application: {str(e)}")

    def load_applications(self):
        self.application_list.clear()
        applications = self.db.get_applications(self.user_id)
        for app in applications:
            self.application_list.addItem(f"{app[2]} - {app[3]} ({app[6]})")  # Company - Position (Date)

    def view_application(self, item):
        try:
            company, rest = item.text().split(" - ")
            position, date = rest.split(" (")
            date = date[:-1]  # Remove the closing parenthesis
            application = self.db.get_application_by_company_position_date(self.user_id, company, position, date)
            if application:
                QMessageBox.information(self, "Application Details",
                                        f"Company: {application[2]}\n"
                                        f"Position: {application[3]}\n"
                                        f"Job Description: {application[4]}\n"
                                        f"Contact Person: {application[5]}\n"
                                        f"Date: {application[6]}")

                # Emit the application_selected signal when the application is viewed
                self.application_selected.emit(str(self.user_id), company, position)
            else:
                QMessageBox.warning(self, "Application Not Found", "The selected application could not be found.")
        except Exception as e:
            logging.error(f"Error viewing application: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred while viewing the application: {str(e)}")

    def delete_application(self):
        current_item = self.application_list.currentItem()
        if current_item:
            try:
                company, rest = current_item.text().split(" - ")
                position, date = rest.split(" (")
                date = date[:-1]  # Remove the closing parenthesis
                reply = QMessageBox.question(self, "Delete Application",
                                             f"Are you sure you want to delete this application?",
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.db.delete_application(self.user_id, company, position, date)
                    self.load_applications()
            except Exception as e:
                logging.error(f"Error deleting application: {str(e)}")
                QMessageBox.critical(self, "Error", f"An error occurred while deleting the application: {str(e)}")
