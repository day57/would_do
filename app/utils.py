# app/utils.py

import uuid
import os
from werkzeug.utils import secure_filename
from flask import url_for, session, current_app
from .extensions import db
from .models import File
from datetime import datetime, timedelta

def generate_token():
    return str(uuid.uuid4())

def save_file(file, user_id, token, expiration_days):
    filename = secure_filename(file.filename)
    user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], user_id)
    os.makedirs(user_folder, exist_ok=True)
    file_path = os.path.join(user_folder, filename)
    file.save(file_path)  # Save the uploaded file
    active_until = datetime.utcnow() + timedelta(days=expiration_days)
    file_extension = os.path.splitext(filename)[1][1:].lower()
    new_file = File(
        name=filename,
        size=os.path.getsize(file_path),
        path=file_path,
        user_id=user_id,
        token=token,
        active_until=active_until,
        file_type=file_extension,
    )
    db.session.add(new_file)
    db.session.commit()
    return filename, os.path.getsize(file_path), file_path


def allowed_file(filename):
    allowed_extensions = get_file_types()
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_types():
    allowed_file_types = current_app.config.get(
        'ALLOWED_FILE_TYPES',
        'jpg, jpeg, png, gif, svg, pdf, doc, docx, xls, xlsx, ppt, pptx, mp3, wav, aac, mp4, avi, mov, txt, js, html, css, zip, rar, py, java, c, cpp, cs, rb, php, sql, xml, json'
    ).split(',')
    allowed_file_types = [file_type.strip().lower().lstrip('.') for file_type in allowed_file_types]
    return allowed_file_types

def build_directory_tree_html(files):
    html = "<ul class='tree'>"
    html += '<li class="root"><input type="checkbox" id="root-folder" hidden>'
    html += '<label for="root-folder"><a href="/">uploads/</a></label> <button class="open-modal-btn" data-modal-target="uploadModal" id="openUploadModalBtn">Upload File</button>'
    for file in files:
        html += f"<li id='tree_li'><a href='/view/{file.token}'>{file.name}</a></li>"
    html += "</ul>"
    return html

def readable_file_size(size):
    size = abs(size)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"
