from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import session
import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
MEDIA_FOLDER = os.path.join(os.getcwd(), "media")
MEDIA = os.path.join("media", "uploads")

app = Flask(__name__)


@app.route("/media/<path:filename>")
def media_files(filename):
    return send_from_directory(MEDIA_FOLDER, filename)


@app.context_processor
def inject_login_status():
    return dict(is_authenticated=("user_id" in session))


@app.context_processor
def inject_logged_user():
    user_id = session.get("user_id")
    if user_id:
        from app.models import User

        user = User.query.get(user_id)
        return dict(user=user)

    return dict(user=None)


@app.context_processor
def inject_order_count():
    from app.models import OrderDetails

    order_count = OrderDetails.query.filter_by(user_id=session.get("user_id")).count()
    return dict(order_count=order_count)


app.secret_key = "my_secret_key_123"
app.config["UPLOAD_FOLDER"] = MEDIA
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:user@localhost/flask_ecommerce"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes

with app.app_context():
    db.create_all()
