# __init__.py at the root of your Flask project
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Import the Blueprint from the module package
    from module import module_blueprint
    
    # Register the Blueprint with the application
    app.register_blueprint(module_blueprint, url_prefix='/module')
    
    return app
