# File Viewer Application

This is a Flask-based web application that allows users to navigate a directory tree and view various types of files, such as images, videos, and code files, directly in the browser. It also provides file information and a download link.

## Features

- Display directory tree with nested folders and files
- View images, videos, and code files
- Show file information (name, size, type)
- Download files

## Prerequisites

- Python 3.x
- Flask

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/would_do.git
   cd file-viewer
   ```

2. **Create a Virtual Environment**

   It is recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   Install the required dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

- Create an `uploads` folder in the root directory of the project. This folder will contain the files and directories you want to view.

  ```bash
  mkdir uploads
  ```

- Place the files and folders you want to view inside the `uploads` directory.

## Running the Application

Start the Flask development server:

```bash
flask run
```

By default, the application will run on `http://127.0.0.1:5000`.

## Usage

1. Open your web browser and navigate to `http://127.0.0.1:5000`.
2. You will see the directory tree on the left side of the page.
3. Click on a file to view its content and information on the right side of the page.
4. You can download the file using the provided download link.

## Directory Structure

```
file-viewer/
├── uploads/
│   ├── folder2/
│   ├── folder3/
│   ├── folder4/
│   ├── example.txt
│   ├── image.png
│   └── video.mp4
├── templates/
│   └── home.html
├── app.py
└── requirements.txt
```

- `uploads/`: Directory containing files and folders to view.
- `templates/`: Directory containing HTML templates.
- `app.py`: Main application file.
- `requirements.txt`: File containing the list of dependencies.

## Customization

You can customize the application by modifying the following:

- **HTML Templates**: Located in the `templates/` directory.
- **CSS Styles**: Inline styles are included in the `home.html` template. You can move these to a separate CSS file if needed.
- **Supported File Types**: Modify the `view_file` route in `app.py` to handle additional file types.

## Future Enhancements

- Integrate with a database to manage files and folders.
- Add support for more file formats.
- Implement user authentication and authorization.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

