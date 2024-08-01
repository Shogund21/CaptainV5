import os
import logging
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import tiktoken

class AIChatBot:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logging.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")
        self.chat_model = ChatOpenAI(temperature=0.7, openai_api_key=self.api_key)
        self.max_tokens = 16000  # Set a limit slightly below the model's maximum
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    def truncate_text(self, text, max_tokens):
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return self.encoding.decode(tokens[:max_tokens])

    def chatbot_response(self, text):
        try:
            truncated_text = self.truncate_text(text, self.max_tokens)
            messages = [
                SystemMessage(content="You are Chief, a helpful AI assistant for job applications and resume analysis."),
                HumanMessage(content=truncated_text)
            ]
            response = self.chat_model.invoke(messages)
            return response.content.strip()
        except Exception as e:
            logging.error(f"Error in chatbot_response: {str(e)}")
            return "I apologize, but I encountered an error while processing your message. Please try again later or contact support if the issue persists."

    def analyze_resume(self, resume_content):
        truncated_content = self.truncate_text(resume_content, self.max_tokens // 2)
        prompt = f"Analyze the following resume and provide a summary of key skills, experience, and areas for improvement:\n\n{truncated_content}"
        return self.chatbot_response(prompt)

    def analyze_application(self, application_content):
        truncated_content = self.truncate_text(application_content, self.max_tokens // 2)
        prompt = f"Analyze the following job application and provide a summary of key requirements and responsibilities:\n\n{truncated_content}"
        return self.chatbot_response(prompt)

    def compare_resume_application(self, resume_content, application_content):
        truncated_resume = self.truncate_text(resume_content, self.max_tokens // 3)
        truncated_application = self.truncate_text(application_content, self.max_tokens // 3)
        prompt = f"Compare the following resume and job application. Identify matches, mismatches, and provide recommendations:\n\nResume:\n{truncated_resume}\n\nJob Application:\n{truncated_application}"
        return self.chatbot_response(prompt)

    def generate_cover_letter(self, resume_content, application_content):
        try:
            truncated_resume = self.truncate_text(resume_content, self.max_tokens // 3)
            truncated_application = self.truncate_text(application_content, self.max_tokens // 3)
            messages = [
                SystemMessage(content="You are Chief, an AI assistant specialized in generating cover letters based on resumes and job applications."),
                HumanMessage(content=f"Generate a cover letter based on this resume:\n\n{truncated_resume}\n\nAnd this job application:\n\n{truncated_application}")
            ]
            response = self.chat_model.invoke(messages)
            return f"Here's the generated cover letter:\n\n{response.content.strip()}"
        except Exception as e:
            logging.error(f"Error in generate_cover_letter: {str(e)}")
            return "I apologize, but I encountered an error while generating the cover letter. Please try again later or contact support if the issue persists."
