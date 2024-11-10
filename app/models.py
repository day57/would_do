from datetime import datetime
from . import db

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    files = db.relationship('File', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    upload_limit = db.Column(db.Integer, nullable=False, default=1000000)

    def __repr__(self):
        return f"<User(id='{self.id}')>"

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.BigInteger, nullable=False)
    path = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(36), unique=True, nullable=False)
    downloads = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)
    download_path = db.Column(db.String(120))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    active_until = db.Column(db.DateTime)
    file_type = db.Column(db.String(120), nullable=False, default='unknown')

    def __repr__(self):
        return f"<File(name='{self.name}', size='{self.size}', path='{self.path}', user_id='{self.user_id}', token='{self.token}')>"
