from flask import Flask, render_template, send_from_directory, url_for
from werkzeug.utils import safe_join
import os

def create_app():
    app = Flask(__name__)

    UPLOAD_FOLDER = 'uploads'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    def get_directory_data():
        return build_directory_tree(app.config['UPLOAD_FOLDER'])

    def build_directory_tree(folder_path):
        tree = {}
        root_files = []
        for root, dirs, files in os.walk(folder_path):
            folder_structure = tree
            relative_path = os.path.relpath(root, folder_path)
            if relative_path == ".":
                relative_path = ""
                root_files.extend(files)
            for part in relative_path.split(os.sep):
                if part not in folder_structure:
                    folder_structure[part] = {}
                folder_structure = folder_structure[part]
            for file in files:
                if relative_path == "":
                    root_files.append(file)
                else:
                    folder_structure[file] = None
        return tree, root_files

    def directory_tree_to_html(tree, root_files, parent_id="", is_root=False):
        html = '<ul class="tree">'
        if is_root:
            html += '<li class="root"><input type="checkbox" id="root-folder" hidden>'
            html += '<label for="root-folder">uploads/</label>'
        for name, subtree in tree.items():
            if subtree is None:
                file_path = os.path.join(parent_id, name).replace("\\", "/")
                html += f'<li><a href="{url_for("view_file", filename=file_path)}">{name}</a></li>'
            else:
                dir_id = os.path.join(parent_id, name).replace("\\", "-").replace("/", "-")
                html += f'<li><input type="checkbox" id="{dir_id}" hidden>'
                html += f'<label for="{dir_id}">{name}/</label>'
                html += directory_tree_to_html(subtree, [], os.path.join(parent_id, name))
                html += '</li>'
        html += '</ul>'
        return html

    def generate_root_files_html(root_files):
        html = '<ul>'
        for file in root_files:
            file_path = file.replace("\\", "/")
            html += f'<li><a href="{url_for("view_file", filename=file_path)}">{file}</a></li>'
        html += '</ul>'
        return html

    def readable_file_size(size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    @app.route('/')
    def home():
        tree, root_files = get_directory_data()
        tree_html = directory_tree_to_html(tree, root_files, is_root=True)
        if root_files:
            tree_html += generate_root_files_html(root_files)
        return render_template('home.html', directory_tree_html=tree_html, content='', file_info=None)

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
                content = f"<img src='/files/{filename}' alt='{filename}'>"
            elif file_type in ['txt', 'py', 'js', 'html', 'css']:
                with open(file_path, 'r') as file:
                    code = file.read()
                    code = code.replace('<', '&lt;').replace('>', '&gt;')  # Escape HTML tags
                    content = f"<pre><code>{code}</code></pre>"
            elif file_type in ['mp4', 'avi']:
                content = f"<video controls><source src='/files/{filename}' type='video/{file_type}'></video>"
            else:
                content = "Unsupported file format"
            
            tree, root_files = get_directory_data()
            tree_html = directory_tree_to_html(tree, root_files, is_root=True)
            if root_files:
                tree_html += generate_root_files_html(root_files)
            
            return render_template('home.html', content=content, file_info=file_info, directory_tree_html=tree_html)
        else:
            return "File not found", 404

    @app.route('/files/<path:filename>')
    def files(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/download/<path:filename>')
    def download_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
