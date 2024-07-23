from flask import Blueprint, render_template, request, send_from_directory
from werkzeug.utils import secure_filename
import os
import pdb
# Create a Blueprint for this module
upload_blueprint = Blueprint('upload', __name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route to handle file uploads
@upload_blueprint.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file part in the request')  # Debugging output
            return 'No file part in the request'
        file = request.files['file']
        if file.filename == '':
            print('No selected file')  # Debugging output
            return 'No selected file'
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            print(f'File {filename} has been uploaded to {file_path}')  # Debugging output
            return 'File has been uploaded'
    return render_template('upload.html')

# Route to display the content of the file
@upload_blueprint.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if os.path.exists(file_path):
        file_type = filename.rsplit('.', 1)[1].lower()
        if file_type in ['png', 'jpg', 'jpeg', 'gif']:
            content = f"<img src='/module/files/{filename}' alt='{filename}'>"
        elif file_type in ['txt', 'py', 'js', 'html', 'css']:
            with open(file_path, 'r') as file:
                content = f"<pre><code>{file.read()}</code></pre>"
        elif file_type in ['mp4', 'avi']:
            content = f"<video controls><source src='/module/files/{filename}' type='video/{file_type}'></video>"
        else:
            content = "Unsupported file format"
        print(f'Rendering content for {filename}')  # Debugging output
        return render_template('home.html', content=content)
    else:
        print(f'File {filename} not found')  # Debugging output
        return "File not found", 404

# Route to serve files from the uploads directory
@upload_blueprint.route('/files/<filename>')
def file(filename):
    print(f'Serving file {filename}')  # Debugging output
    return send_from_directory(UPLOAD_FOLDER, secure_filename(filename))
