from flask import Flask, render_template, send_from_directory, url_for
from werkzeug.utils import safe_join
import os

def create_app():
    app = Flask(__name__)
    UPLOAD_FOLDER = 'uploads'  # Directory for uploaded files
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Function to get directory data in a tree structure
    def get_directory_data():
        return build_directory_tree(app.config['UPLOAD_FOLDER'])

    # Function to build a directory tree structure
    def build_directory_tree(folder_path):
        tree = {}
        for root, dirs, files in os.walk(folder_path):
            folder_structure = tree
            relative_path = os.path.relpath(root, folder_path)
            if relative_path != ".":
                for part in relative_path.split(os.sep):
                    if part not in folder_structure:
                        folder_structure[part] = {}
                    folder_structure = folder_structure[part]
            for file in files:
                folder_structure[file] = os.path.join(relative_path, file).replace("\\", "/")
        return tree

    # Function to convert the directory tree structure to HTML
    def directory_tree_to_html(tree, parent_id="", is_root=False):
        html = '<ul class="tree">'
        if is_root:
            html += '<li class="root"><input type="checkbox" id="root-folder" hidden>'
            html += '<label for="root-folder"><a href="/">uploads /</a></label>'
        
        has_content = False  # Flag to check if there are any directories or files

        #where we are viisually making the tree items
        for name, subtree in tree.items():
            has_content = True  # Set flag to True if there is content
            if isinstance(subtree, str):
                file_path = subtree.replace("\\", "/")
                html += f'<li><a href="{url_for("view_file", filename=file_path)}">{name}</a></li>'
            else:
                dir_id = os.path.join(parent_id, name).replace("\\", "-").replace("/", "-")
                html += f'<li><input type="checkbox" id="{dir_id}" hidden>'
                html += f'<label for="{dir_id}">{name} /</label>'
                html += directory_tree_to_html(subtree, os.path.join(parent_id, name))
                html += '</li>'
        
        html += '</ul>'
        return html

    # Function to format file size into a readable string
    def readable_file_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    # Route for the home page
    @app.route('/')
    def home():
        tree = get_directory_data()
        tree_html = directory_tree_to_html(tree, is_root=True)
        
        # Check if the root directory is empty
        is_root_empty = not any(tree)
        
        return render_template('home.html', directory_tree_html=tree_html, content='', file_info=None, is_root_empty=is_root_empty)

    # Route to view a specific file
    @app.route('/view/<path:filename>')
    def view_file(filename):
        file_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
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
            
            tree = get_directory_data()
            tree_html = directory_tree_to_html(tree, is_root=True)
            
            return render_template('home.html', content=content, file_info=file_info, directory_tree_html=tree_html, is_root_empty=False)
        else:
            return "File not found", 404

    # Route to serve static files
    @app.route('/files/<path:filename>')
    def files(filename):
        file_path = safe_join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        else:
            return "File not found", 404

    # Route to download a specific file
    @app.route('/download/<path:filename>')
    def download_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
