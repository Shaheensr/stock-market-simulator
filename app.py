import flask

app = flask.Flask(__name__)

@app.route("/")
def home():
    return "Hello World"

app.run()