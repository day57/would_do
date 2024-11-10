from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_apscheduler import APScheduler

db = SQLAlchemy()
migrate = Migrate()
session = Session()
csrf = CSRFProtect()
scheduler = APScheduler()
