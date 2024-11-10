from flask import current_app
from .extensions import scheduler, db
from .models import File
from datetime import datetime
import os

def delete_expired_files():
    with scheduler.app.app_context():
        now = datetime.utcnow()
        expired_files = File.query.filter(File.active_until < now).all()
        for file in expired_files:
            try:
                os.remove(file.path)
            except OSError:
                pass
            db.session.delete(file)
        db.session.commit()

def init_scheduler(app):
    scheduler.init_app(app)
    scheduler.start()

    # Schedule the task
    scheduler.add_job(
        id='delete_expired_files',
        func=delete_expired_files,
        trigger='interval',
        minutes=60
    )

