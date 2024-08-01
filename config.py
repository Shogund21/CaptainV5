import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DATABASE_URI = os.getenv('DATABASE_URI', 'captain1.db')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

config = Config()