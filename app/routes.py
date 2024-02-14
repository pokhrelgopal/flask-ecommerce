from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import app, db
from app.models import User, Todo
from functools import wraps
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.join("media", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        else:
            error = "Invalid username or password"
            return render_template("login.html", error=error)
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        eu = existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if not eu:
            new_user = User(username=username, email=email)
            new_user.password = password
            db.session.add(new_user)
            db.session.commit()

            flash("User created successfully!", "success")
            return redirect(url_for("login"))
        else:
            error = "Username or email already exists"
            return render_template("register.html", error=error)
    return render_template("register.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)
        todos = user.todos

        if request.method == "POST":
            title = request.form.get("taskInput")
            image_file = request.files.get("my_image")

            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            else:
                image_path = None
            image_path = image_path.replace("\\", "/")
            new_todo = Todo(title=title, user_id=user_id, image=image_path)
            db.session.add(new_todo)
            db.session.commit()
            todos = user.todos

            flash("New task added successfully!", "success")
            print(todos)
        return render_template("index.html", user=user, todos=todos)

    else:
        return redirect(url_for("login"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" in session:
        user_id = session["user_id"]
        user = User.query.get(user_id)

        task = Todo.query.get(task_id)

        if task and task.user_id == user.id:
            db.session.delete(task)
            db.session.commit()
            flash("Task deleted successfully!", "success")

            return redirect(url_for("index"))

    return redirect(url_for("index"))
