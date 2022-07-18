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
import rsa
import base64

from sqlalchemy import true

app = flask.Flask(__name__)

uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("FLASK_SECRET_KEY")

login_manager = LoginManager()
login_manager.init_app(app)


db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)


db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def home():
    return flask.render_template("index.html")

@app.route("/login")
def login():
    return flask.render_template("login.html")

@app.route("/login", methods = ['POST'])
def login_post():
    username = flask.request.form.get("username")
    inputPassword = flask.request.form.get("password")
    encryptedPassword = rsa.encrypt(inputPassword.encode(), os.getenv("PUBLIC_KEY"))
    user = db.session.query(User).filter_by(username=username, password=encryptedPassword).first()

    if user is None:
        flask.flash("Incorrect Username or Password.")
        flask.redirect(flask.url_for("login"))
    else:
        login_user(user)
        next = flask.request.args.get("next")

        return flask.redirect(next or flask.url_for("home"))

@app.route("/register")
def register():
    return flask.render_template("register.html")

@app.route("/register", methods = ['POST'])
def register_post():
    checkQuery = (
        db.session.query(User)
        .filter_by(username=flask.request.form.get("username"))
        .count()
    )

    if checkQuery > 0:
        flask.flash("Username is already taken.")
        return flask.redirect(flask.url_for("register"))

    password = flask.request.form.get("password")
    encryptedPassword = rsa.encrypt(password.encode(), os.getenv("PUBLIC_KEY"))
    user = User(username=flask.request.form.get("username"), password=encryptedPassword)
    db.session.add(user)
    db.session.commit()

    return flask.redirect(flask.url_for("login"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return flask.redirect(flask.url_for("index"))

app.run(debug=true)