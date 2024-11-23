import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")


@app.route("/")
def index():
    return "<h1>Hello, World!</h1>"
