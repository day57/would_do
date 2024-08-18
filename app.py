from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, flash, jsonify
from werkzeug.utils import secure_filename, safe_join
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import uuid
import os
from dotenv import load_dotenv


# configuration
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
app.config['MAX_CONTENT_LENGTH'] = 5400 * 1024 * 1024  # 5400 MB in bytes
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
Session(app)

# Ensure the shared upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUIDs are 36 chars long
    files = db.relationship('File', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    upload_limit = db.Column(db.Integer, nullable=False, default=1000000)  # Default upload limit in bytes

    def __repr__(self):
        return f"<User(id='{self.id}')>"


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    path = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(36), unique=True, nullable=False)
    downloads = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)
    download_path = db.Column(db.String(120))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    active_until = db.Column(db.DateTime)

    def __repr__(self):
        return f"<File(name='{self.name}', size='{self.size}', path='{self.path}', user_id='{self.user_id}', token='{self.token}')>"

def generate_token():
    return str(uuid.uuid4())

def get_file_types():
    allowed_file_types = os.getenv('ALLOWED_FILE_TYPES', 'jpg, png, pdf, docx').split(', ')
    return allowed_file_types

def save_file(file, user_id, token, expiration_days):
    filename = secure_filename(file.filename)
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, filename)
    file.save(file_path)

    # Calculate the expiration date
    active_until = datetime.utcnow() + timedelta(days=expiration_days)

    # Save file metadata in the database with the token and expiration date
    new_file = File(
        name=filename,
        size=os.path.getsize(file_path),
        path=file_path,
        user_id=user_id,
        token=token,
        active_until=active_until
    )
    db.session.add(new_file)
    db.session.commit()

    return filename, os.path.getsize(file_path), file_path  # Return these values if needed elsewhere




@app.route('/delete/<token>', methods=['POST'])
def delete_file(token):
    file = File.query.filter_by(token=token).first()
    if file:
        try:
            os.remove(file.path)
            db.session.delete(file)
            db.session.commit()
            return jsonify({'success': True, 'message': 'File deleted successfully.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    return jsonify({'success': False, 'message': 'File not found.'}), 404



@app.before_request
def before_request():
    if not hasattr(app, 'db_initialized'):
        with app.app_context():
            db.create_all()
        app.db_initialized = True


def delete_expired_files():
    now = datetime.utcnow()
    expired_files = File.query.filter(File.active_until < now).all()
    for file in expired_files:
        try:
            os.remove(file.path)
        except OSError:
            pass
        db.session.delete(file)
    db.session.commit()


@app.route('/')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return render_template('index.html')
    else:
        user = User.query.get(user_id)
        files = user.files  # Assuming the relationship is set to load the files
        directory_tree_html = build_directory_tree_html(files)
        return render_template('files.html', user_id=user_id, directory_tree_html=directory_tree_html, file_info=None, content=None)

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

    if 'file' not in request.files or 'expiration' not in request.form:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    # Get the selected expiration time from the form
    expiration_days = int(request.form.get('expiration', 1))  # Default to 1 day if not specified

    token = generate_token()
    filename, size, file_path = save_file(file, user_id, token, expiration_days)
    
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/files/<token>')
def files(token):
    file = File.query.filter_by(token=token).first()
    if file and session.get('user_id') == file.user_id:
        return send_from_directory(os.path.dirname(file.path), os.path.basename(file.path))
    else:
        return "File not found", 404

@app.route('/view/<token>')
def view_file(token):
    file = File.query.filter_by(token=token).first()
    if file and session.get('user_id') == file.user_id:
        file_path = file.path
        if os.path.exists(file_path):
            file_info = {
                "name": os.path.basename(file_path),
                "size": readable_file_size(os.path.getsize(file_path)),
                "type": file.name.rsplit('.', 1)[1].lower(),
                "path": file.name,
                "token": file.token  # Ensure this is added to pass to the template
            }

            file_type = file_info["type"]
            if file_type in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                content = f"<img src='{url_for('files', token=token)}' alt='{file.name}'>"
            elif file_type in ['txt', 'py', 'js', 'html', 'css', 'cpp', 'md']:
                with open(file_path, 'r') as file:
                    code = file.read()
                    code = code.replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML tags
                    content = f"<pre><code>{code}</code></pre>"
            elif file_type in ['mp4', 'avi']:
                content = f"<video controls><source src='{url_for('files', token=token)}' type='video/{file_type}'></video>"
            else:
                content = "<div><p>Unsupported file format</p></div>"
            
            files = File.query.filter_by(user_id=session.get('user_id')).all()
            directory_tree_html = build_directory_tree_html(files)
            
            return render_template('files.html', user_id=session.get('user_id'), content=content, file_info=file_info, directory_tree_html=directory_tree_html, is_root_empty=False)
        else:
            return "File not found", 404
    else:
        return "File not found", 404

@app.route('/download/<token>')
def download_file(token):
    file = File.query.filter_by(token=token).first()
    if file and session.get('user_id') == file.user_id:
        return send_from_directory(os.path.dirname(file.path), os.path.basename(file.path), as_attachment=True)
    else:
        return "File not found", 404

def build_directory_tree_html(files):
    html = "<ul class='tree'>"
    html += '<li class="root"><input type="checkbox" id="root-folder" hidden>'
    html += '<label for="root-folder"><a href="/">uploads/</a></label> <button id="uploadBtn">Upload File</button>'
    for file in files:
        html += f"<li id=tree_li><a href='/view/{file.token}'>{file.name}</a></li>"
    html += "</ul>"
    return html
    
def readable_file_size(size):
    # Convert file size to a readable format
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

if __name__ == '__main__':
    app.run(debug=True)
