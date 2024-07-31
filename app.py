from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, make_response
from werkzeug.utils import secure_filename, safe_join
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_PATH'] = 1000000  # Max file size, adjust as needed
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'supersecretkey'  # Use a strong secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Session(app)

# Ensure the shared upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUIDs are 36 chars long
    files = db.relationship('File', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.id}')"

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"File('{self.name}', '{self.size}', '{self.path}', '{self.user_id}')"

def save_file(file, user_id):
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return filename, os.path.getsize(file_path), file_path

@app.before_request
def before_request():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
        app.db_initialized = True

@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('index.html')
    else:
        user = User.query.get(user_id)
        files = File.query.filter_by(user_id=user_id).all()
        directory_tree_html = build_directory_tree_html(files)
        return render_template('welcome.html', user_id=user_id, directory_tree_html=directory_tree_html, file_info=None, content=None)

@app.route('/create_user', methods=['POST'])
def create_user():
    user_id = session.get('user_id')
    if not user_id:
        user_id = str(uuid.uuid4())
        session['user_id'] = user_id
        new_user = User(id=user_id)
        db.session.add(new_user)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))

    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    filename, size, file_path = save_file(file, user_id)
    new_file = File(name=filename, size=size, path=file_path, user_id=user_id)
    db.session.add(new_file)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/files/<filename>')
def files(filename):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))
    file = File.query.filter_by(name=filename, user_id=user_id).first()
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else:
        return "File not found", 404

@app.route('/view/<path:filename>')
def view_file(filename):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))
    
    file = File.query.filter_by(name=filename, user_id=user_id).first()
    if file:
        file_path = file.path
        if os.path.exists(file_path):
            file_info = {
                "name": os.path.basename(file_path),
                "size": readable_file_size(os.path.getsize(file_path)),
                "type": filename.rsplit('.', 1)[1].lower(),
                "path": filename
            }
            file_type = file_info["type"]
            if file_type in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                content = f"<img src='{url_for('files', filename=filename)}' alt='{filename}'>"
            elif file_type in ['txt', 'py', 'js', 'html', 'css', 'cpp', 'md']:
                with open(file_path, 'r') as file:
                    code = file.read()
                    code = code.replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML tags
                    content = f"<pre><code>{code}</code></pre>"
            elif file_type in ['mp4', 'avi']:
                content = f"<video controls><source src='{url_for('files', filename=filename)}' type='video/{file_type}'></video>"
            else:
                content = "<div><p>Unsupported file format</p></div>"
            
            user = User.query.get(user_id)
            files = File.query.filter_by(user_id=user_id).all()
            directory_tree_html = build_directory_tree_html(files)
            
            return render_template('welcome.html', content=content, file_info=file_info, directory_tree_html=directory_tree_html, is_root_empty=False)
        else:
            return "File not found", 404
    else:
        return "File not found", 404

@app.route('/download/<path:filename>')
def download_file(filename):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('index'))
    file = File.query.filter_by(name=filename, user_id=user_id).first()
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        return "File not found", 404

def build_directory_tree_html(files):
    tree_html = '<ul>'
    for file in files:
        tree_html += f'<li><a href="{url_for("view_file", filename=file.name)}">{file.name}</a></li>'
    tree_html += '</ul>'
    return tree_html

def readable_file_size(size):
    # Helper function to convert file size into a readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

if __name__ == '__main__':
    app.run(debug=True)
