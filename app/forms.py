# app/forms.py

from flask_wtf import FlaskForm
from wtforms import SubmitField

class CreateUserForm(FlaskForm):
    submit = SubmitField('Create User')
