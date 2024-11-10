import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    MAX_CONTENT_LENGTH = 5400 * 1024 * 1024
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_FILE_SIZE = 5400 * 1024 * 1024
    SCHEDULER_API_ENABLED = True
