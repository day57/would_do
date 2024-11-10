# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, send_from_directory, current_app
from .forms import CreateUserForm
from .extensions import db
from .models import User, File
from .utils import (
    allowed_file,
    get_file_types,
    generate_token,
    save_file,
    readable_file_size,
    build_directory_tree_html,
)
import uuid
import os

import logging

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = CreateUserForm()  # Create the form
    if form.validate_on_submit():
        return redirect(url_for('main.create_user'))

    user_id = session.get('user_id')
    if not user_id:
        # No user in session, render the welcome page with the form
        return render_template('index.html', form=form)
    else:
        user = User.query.get(user_id)
        if not user:
            # If the user ID in the session doesn't exist in the database, render the welcome page
            return render_template('index.html', form=form)

        # If the user exists, render the main file explorer page
        files = File.query.filter_by(user_id=user_id).all()
        directory_tree_html = build_directory_tree_html(files)
        return render_template('files.html', user_id=user_id, directory_tree_html=directory_tree_html, file_info=None, content=None, form=form)  # Pass form to the template

@main.route('/create_user', methods=['POST'])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())  # Generate a new unique user ID
            session['user_id'] = user_id  # Store the user ID in the session
            new_user = User(id=user_id)  # Create a new User object
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': True, 'message': 'User created successfully.'}), 200
        else:
            return jsonify({'success': False, 'message': 'User already exists.'}), 400
    # If form validation fails
    return jsonify({'success': False, 'message': 'Invalid form submission.'}), 400

@main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))

@main.route('/upload', methods=['POST'])
def upload():
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part in the request.'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file.'}), 400

    # Validate file extension
    if not allowed_file(file.filename):
        allowed_extensions = ", ".join(get_file_types())
        return jsonify({'success': False, 'message': f'File type not allowed. Allowed types: {allowed_extensions}.'}), 400

    # Validate file size
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0, 0)  # Reset file pointer
    if file_length > current_app.config['MAX_FILE_SIZE']:
        return jsonify({'success': False, 'message': 'File exceeds the maximum allowed size.'}), 400

    expiration_days = int(request.form.get('expiration', 1))  # Default to 1 day
    token = generate_token()

    try:
        filename, size, file_path = save_file(file, user_id, token, expiration_days)
        message = f'File "{filename}" uploaded successfully.'
        return jsonify({'success': True, 'message': message}), 200
    except Exception as e:
        # Log the exception as needed
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

@main.route('/delete/<token>', methods=['POST'])
def delete_file(token):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'User not logged in.'}), 401

    file = File.query.filter_by(token=token, user_id=user_id).first()
    if file:
        try:
            if os.path.exists(file.path):
                os.remove(file.path)
            db.session.delete(file)
            db.session.commit()
            return jsonify({'success': True, 'message': 'File deleted successfully.'}), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'Error deleting file: {str(e)}'}), 500
    else:
        return jsonify({'success': False, 'message': 'File not found.'}), 404
    
@main.route('/files/<token>')
def files(token):
    user_id = session.get('user_id')
    file = File.query.filter_by(token=token, user_id=user_id).first()
    if file:
        return send_from_directory(os.path.dirname(file.path), os.path.basename(file.path))
    else:
        return "File not found", 404


@main.route('/view/<token>')
def view_file(token):
    user_id = session.get('user_id')
    if not user_id:
        logging.warning(f"View attempt without user session. Token: {token}")
        return "User not logged in.", 401

    file = File.query.filter_by(token=token, user_id=user_id).first()
    if file:
        file_path = file.path
        if os.path.exists(file_path):
            file_info = {
                "name": os.path.basename(file_path),
                "size": readable_file_size(os.path.getsize(file_path)),
                "type": file.name.rsplit('.', 1)[1].lower(),
                "path": file.name,
                "token": file.token,
                "uploaded_at": file.uploaded_at,
                "active_until": file.active_until,
            }

            file_type = file_info["type"]
            content = None
            if file_type in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                content = f"<img src='{url_for('main.files', token=token)}' alt='{file.name}'>"
                logging.info(f"Displaying image: {file.path}")
            elif file_type in ['txt', 'py', 'js', 'html', 'css', 'cpp', 'md', 'java', 'c', 'cs', 'rb', 'php', 'sql', 'json', 'xml']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                        code = code.replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML tags
                        content = f"<pre><code>{code}</code></pre>"
                        logging.info(f"Displaying code: {file.path}")
                except Exception as e:
                    content = f"<p>Error reading file: {str(e)}</p>"
                    logging.error(f"Error reading file {file.path}: {e}")
            elif file_type in ['mp4', 'avi', 'mov']:
                content = f"<video controls><source src='{url_for('main.files', token=token)}' type='video/{file_type}'></video>"
                logging.info(f"Displaying video: {file.path}")
            elif file_type in ['mp3', 'wav', 'aac']:
                content = f"<audio controls><source src='{url_for('main.files', token=token)}' type='audio/{file_type}'></audio>"
                logging.info(f"Displaying audio: {file.path}")
            elif file_type == 'pdf':
                content = f"<embed src='{url_for('main.files', token=token)}' width='100%' height='600px' type='application/pdf'>"
                logging.info(f"Displaying PDF: {file.path}")
            else:
                content = "<div><p>Unsupported file format</p></div>"
                logging.warning(f"Unsupported file type: {file.type}")

            files = File.query.filter_by(user_id=user_id).all()
            directory_tree_html = build_directory_tree_html(files)

            return render_template(
                'files.html',
                user_id=user_id,
                content=content,
                file_info=file_info,
                directory_tree_html=directory_tree_html,
                is_root_empty=False
            )
        else:
            logging.error(f"File does not exist on server: {file.path}")
            return "File not found", 404
    else:
        logging.error(f"No file found with token: {token} for user: {user_id}")
        return "File not found", 404



@main.route('/download/<token>')
def download_file(token):
    user_id = session.get('user_id')
    file = File.query.filter_by(token=token, user_id=user_id).first()
    if file:
        if os.path.exists(file.path):
            return send_from_directory(os.path.dirname(file.path), os.path.basename(file.path), as_attachment=True)
        else:
            return jsonify({'success': False, 'message': 'File not found on server.'}), 404
    else:
        return jsonify({'success': False, 'message': 'File not found.'}), 404
