from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

# ! Yo folder bata frontend lai media file serve garne ho
MEDIA_FOLDER = os.path.join(os.getcwd(), "media")

# ! Yo folder ma media file haru upload huncha
MEDIA = os.path.join("media", "uploads")


app = Flask(__name__)


# ! Yaha bata media file serve garne ho img url ma
@app.route("/media/<path:filename>")
def media_files(filename):
    return send_from_directory(MEDIA_FOLDER, filename)


app.secret_key = "my_secret_key_123"
app.config["UPLOAD_FOLDER"] = MEDIA
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:user@localhost/flask_auth"

db = SQLAlchemy(app)

from app import routes

with app.app_context():
    db.create_all()
