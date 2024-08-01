import speech_recognition as sr
import pyttsx3
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

class AIChatTab(QWidget):
    def __init__(self, chatbot, db):
        super().__init__()
        self.chatbot = chatbot
        self.db = db
        self.current_resume = None
        self.current_application = None
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.init_ui()

    def set_current_resume(self, user_id, filename):
        try:
            resume = self.db.get_resume_by_filename(user_id, filename)
            if resume:
                # Try different encodings
                encodings = ['utf-8', 'iso-8859-1', 'windows-1252']
                for encoding in encodings:
                    try:
                        self.current_resume = resume[3].decode(encoding) if isinstance(resume[3], bytes) else resume[3]
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError(
                        f"Unable to decode resume content with any of the attempted encodings: {encodings}")

                self.chat_history.append("Chief: Resume loaded for analysis.")
                self.analyze_resume()
            else:
                raise ValueError("Resume not found.")
        except Exception as e:
            logging.error(f"Error setting current resume: {str(e)}", exc_info=True)
            self.chat_history.append(f"Chief: Error loading resume: {str(e)}")

    def set_current_application(self, user_id, company, position):
        try:
            application = self.db.get_application_by_company_position(user_id, company, position)
            if application:
                self.current_application = application[4]  # Assuming job description is at index 4
                self.chat_history.append("Chief: Job application loaded for analysis.")
                self.analyze_application()
            else:
                raise ValueError("Application not found.")
        except Exception as e:
            logging.error(f"Error setting current application: {str(e)}", exc_info=True)
            self.chat_history.append(f"Chief: Error loading application: {str(e)}")

    def init_ui(self):
        layout = QVBoxLayout()

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        layout.addWidget(send_button)

        analyze_resume_button = QPushButton("Analyze Resume")
        analyze_resume_button.clicked.connect(self.analyze_resume)
        layout.addWidget(analyze_resume_button)

        analyze_application_button = QPushButton("Analyze Job Application")
        analyze_application_button.clicked.connect(self.analyze_application)
        layout.addWidget(analyze_application_button)

        compare_button = QPushButton("Compare Resume and Application")
        compare_button.clicked.connect(self.compare_resume_application)
        layout.addWidget(compare_button)

        self.setLayout(layout)

    def send_message(self):
        user_message = self.input_field.text()
        self.input_field.clear()
        self.chat_history.append(f"You: {user_message}")

        try:
            chief_response = self.chatbot.chatbot_response(user_message)
            # Remove "Chief:" if it's at the beginning of the response
            if chief_response.startswith("Chief:"):
                chief_response = chief_response[6:].strip()
            self.chat_history.append(f"Chief: {chief_response}")
            self.speak_text(chief_response)
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.chat_history.append(f"Chief: {error_message}")
            logging.error(f"Error in chatbot response: {str(e)}")

    def recognize_speech(self):
        with sr.Microphone() as source:
            self.chat_history.append("Listening...")
            try:
                audio = self.recognizer.listen(source)
                user_message = self.recognizer.recognize_google(audio)
                self.chat_history.append(f"You: {user_message}")
                self.send_message(user_message)
            except sr.UnknownValueError:
                self.chat_history.append("Chief: Sorry, I could not understand your speech.")
                self.speak_text("Sorry, I could not understand your speech.")
            except sr.RequestError as e:
                self.chat_history.append(f"Chief: Could not request results from the speech recognition service: {str(e)}")
                self.speak_text(f"Could not request results from the speech recognition service: {str(e)}")
            except Exception as e:
                self.chat_history.append(f"Chief: An error occurred while recognizing speech: {str(e)}")
                logging.error(f"Error in speech recognition: {str(e)}")

    def speak_text(self, text):
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logging.error(f"Error in text-to-speech: {str(e)}")
            self.chat_history.append(f"Chief: Error in text-to-speech: {str(e)}")

    def analyze_resume(self):
        if self.current_resume:
            analysis = self.chatbot.analyze_resume(self.current_resume)
            self.chat_history.append(f"Chief: {analysis}")
        else:
            self.chat_history.append("Chief: No resume loaded. Please select a resume first.")

    def analyze_application(self):
        if self.current_application:
            analysis = self.chatbot.analyze_application(self.current_application)
            self.chat_history.append(f"Chief: {analysis}")
        else:
            self.chat_history.append("Chief: No job application loaded. Please select an application first.")

    def compare_resume_application(self):
        if self.current_resume and self.current_application:
            comparison = self.chatbot.compare_resume_application(self.current_resume, self.current_application)
            self.chat_history.append(f"Chief: {comparison}")
        else:
            self.chat_history.append("Chief: Both resume and job application need to be loaded for comparison.")

    def generate_cover_letter(self, user_id, filename):
        try:
            if self.current_resume and self.current_application:
                # Example of cover letter generation logic
                cover_letter = f"Dear Hiring Manager,\n\nI am writing to express my interest in the {filename} position at your esteemed company. Based on my resume and the job application, I believe I am a strong fit for this role. Please find my detailed resume and application attached for your consideration.\n\nSincerely,\n[Your Name]"
                self.chat_history.append(f"Chief: {cover_letter}")
                logging.info("Cover letter generated.")
                self.speak_text("Cover letter generated.")
            else:
                raise ValueError("Both resume and job application must be loaded before generating a cover letter.")
        except Exception as e:
            logging.error(f"Error generating cover letter: {str(e)}")
            self.chat_history.append(f"Chief: Error generating cover letter: {str(e)}")
            self.speak_text(f"Error generating cover letter: {str(e)}")
