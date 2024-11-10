# app/__init__.py
from flask import Flask
import os
from dotenv import load_dotenv
from .extensions import db, migrate, session, csrf
from .scheduler import init_scheduler  # Import your scheduler initialization function

load_dotenv()

class Config:
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = 5400 * 1024 * 1024  # 5400MB
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'flask_session')
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'your-secret-key')  # Replace with a secure key
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///your_database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_FILE_SIZE = 5400 * 1024 * 1024
    SCHEDULER_API_ENABLED = True
    WTF_CSRF_ENABLED = True

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    session.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection

    # Initialize the scheduler
    init_scheduler(app)

    # Ensure the upload folder and session directory exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

    # Register Blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

app = create_app()
