import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    logout_user,
    login_user,
    current_user,
    login_required,
)
import os
import json

app = flask.Flask(__name__)

@app.route("/")
def home():
    return "Hello World"

app.run()