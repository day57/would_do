from flask import Blueprint

# Create a Blueprint for this module
upload_blueprint = Blueprint('module', __name__)

from . import upload  # Importing upload here to register routes with the Blueprint
