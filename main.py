import sys
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox, QDialog
from ui_components import LoginDialog, RegistrationDialog, ResumeManagementTab, ApplicationTrackingTab
from ai_chat_tab import AIChatTab
from modules.user_management import UserManagement
from modules.database import Database
from ai_chat import AIChatBot

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class CAPTAINApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManagement()
        self.db = Database()
        self.current_user_id = None
        self.chatbot = AIChatBot()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("CAPTAIN")
        self.setGeometry(100, 100, 800, 600)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

    def setup_tabs(self):
        self.tab_widget.clear()
        resume_tab = ResumeManagementTab(user_id=self.current_user_id, database=self.db, parent=self.tab_widget)
        application_tab = ApplicationTrackingTab(self.current_user_id, self.db)
        ai_chat_tab = AIChatTab(self.chatbot, self.db)

        resume_tab.resume_selected.connect(ai_chat_tab.set_current_resume)
        application_tab.application_selected.connect(ai_chat_tab.set_current_application)
        resume_tab.cover_letter_requested.connect(ai_chat_tab.generate_cover_letter)

        self.tab_widget.addTab(resume_tab, "Resume Management")
        self.tab_widget.addTab(application_tab, "Application Tracking")
        self.tab_widget.addTab(ai_chat_tab, "AI Chat")

    def show_login_dialog(self):
        logging.info("Showing login dialog")
        dialog = LoginDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            logging.info(f"Login attempt for user: {username}")
            success, user = self.user_manager.authenticate_user(username, password)
            if success:
                self.current_user_id = user[0]  # Assuming user id is at index 0
                logging.info(f"Login successful for user: {username}")
                QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
                self.setup_tabs()
            else:
                logging.warning(f"Login failed for user: {username}")
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
                self.show_login_dialog()
        else:
            logging.info("Login dialog cancelled")
            self.close()  # Close the application if login is cancelled

    def show_registration_dialog(self):
        dialog = RegistrationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            username = dialog.username_input.text()
            password = dialog.password_input.text()
            success, message = self.user_manager.register_user(username, password)
            if success:
                QMessageBox.information(self, "Registration Successful", message)
                self.show_login_dialog()
            else:
                QMessageBox.warning(self, "Registration Failed", message)
                self.show_registration_dialog()

def main():
    app = QApplication(sys.argv)
    main_window = CAPTAINApp()
    main_window.show()
    main_window.show_login_dialog()  # Display the login dialog
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
