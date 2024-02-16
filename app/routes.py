from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import app, db
from app.models import User, Product, Billing, OrderDetails
import requests
from werkzeug.utils import secure_filename
import os
import json

UPLOAD_FOLDER = os.path.join("media", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def is_authenticated():
    return True if "user_id" in session else False


def is_admin():
    if not is_authenticated():
        return False
    user = User.query.filter_by(id=session["user_id"]).first()
    return True if user.role == "admin" else False


@app.route("/login", methods=["GET", "POST"])
def login():

    if is_authenticated():
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            return redirect(url_for("index"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if is_authenticated():
        return redirect(url_for("index"))
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Passwords do not match.", "warning")
        if len(full_name) < 3:
            flash("Full name must be at least 3 characters long.", "warning")
            return redirect(url_for("register"))
        if len(email) < 6:
            flash("Please enter a valid email.", "warning")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User already exists.", "warning")
            return redirect(url_for("register"))
        user = User(full_name=full_name, email=email)
        user.password = password
        db.session.add(user)
        db.session.commit()
        flash("User created successfully.", "success")
        return redirect(url_for("login"))
    return render_template("auth/register.html")


@app.route("/", methods=["GET", "POST"])
def index():
    status = is_authenticated()
    return render_template("index.html", status=status)


@app.route("/products", methods=["GET", "POST"])
def products():
    status = is_authenticated()
    q = request.args.get("q")
    if q:
        products = Product.query.filter(Product.name.contains(q)).all()
        return render_template("products.html", status=status, products=products)
    products = Product.query.all()
    return render_template("products.html", status=status, products=products)


@app.route("/cart", methods=["GET", "POST"])
def cart():
    status = is_authenticated()
    if not status:
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))
    return render_template("cart.html", status=status)


@app.route("/checkout/<int:product_id>", methods=["GET", "POST"])
def checkout(product_id):
    status = is_authenticated()
    if not status:
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))
    product = Product.query.filter_by(id=product_id).first()

    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        address = request.form.get("address1")
        address2 = request.form.get("address2")
        city = request.form.get("city")
        state = request.form.get("state")
        amount = product.price

        my_billing = Billing(
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            address2=address2,
            city=city,
            state=state,
            amount=amount,
        )
        db.session.add(my_billing)
        db.session.commit()

        my_order = OrderDetails(
            product_id=product.id, billing_id=my_billing.id, user_id=session["user_id"]
        )
        db.session.add(my_order)
        db.session.commit()

        # ! Payment Gateway Integration
        URL = "https://a.khalti.com/api/v2/epayment/initiate/"
        payload = json.dumps(
            {
                "return_url": "http://localhost:5000",
                "website_url": "http://localhost:5000",
                "amount": amount,
                "purchase_order_id": my_order.id,
                "purchase_order_name": product.name,
            }
        )
        headers = {"Authorization": "Key dbf107a9c72548468029bdf82a8335de"}
        response = requests.post(URL, data=payload, headers=headers)
        # ! NOTE :: Manage the response from the payment gateway

        flash("Order placed successfully.", "success")
        return redirect(url_for("orders"))

    return render_template("checkout.html", status=status, product=product)


@app.route("/orders", methods=["GET", "POST"])
def orders():
    status = is_authenticated()
    if not status:
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))
    orders = OrderDetails.query.filter_by(user_id=session["user_id"]).all()
    return render_template("orders.html", status=status, orders=orders)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    status = is_authenticated()
    if not status:
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))
    profile = User.query.filter_by(id=session["user_id"]).first()

    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if len(full_name) < 5:
            flash("Proper full name is required.", "warning")
            return redirect(url_for("profile"))
        if len(email) < 6:
            flash("Please enter a valid email.", "warning")
            return redirect(url_for("profile"))
        if not password and not confirm_password:
            new_user = User.query.filter_by(id=session["user_id"]).first()
            new_user.full_name = full_name
            new_user.email = email
            db.session.commit()
            flash("Profile updated successfully.", "success")

        if password or confirm_password:
            if len(password) < 6:
                flash("Password must be at least 6 characters long.", "warning")
                return redirect(url_for("profile"))
            if password != confirm_password:
                flash("Passwords do not match.", "warning")
                return redirect(url_for("profile"))
            new_user = User.query.filter_by(id=session["user_id"]).first()
            new_user.full_name = full_name
            new_user.email = email
            new_user.password = password
            db.session.commit()
            flash("Profile updated successfully.", "success")

    return render_template("profile.html", status=status, profile=profile)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    admin = is_admin()
    if not admin:
        flash("You are not authorized to access admin page.", "warning")
        return redirect(url_for("login"))
    return render_template("admin/dashboard.html")


@app.route("/admin-products", methods=["GET", "POST"])
def admin_products():
    status = is_authenticated()
    if not is_admin():
        flash("You are not authorized to access admin page.", "warning")
        return redirect(url_for("login"))
    if not status:
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))

    products = Product.query.all()

    if request.method == "POST":
        name = request.form.get("product_name")
        price = request.form.get("product_price")
        image_file = request.files["product_image"]
        description = request.form.get("product_description")

        if not name:
            flash("Product name is required.", "warning")
            return redirect(url_for("admin_products"))

        if not price:
            flash("Product price is required.", "warning")
            return redirect(url_for("admin_products"))

        if not description:
            flash("Product description is required.", "warning")
            return redirect(url_for("admin_products"))

        if not image_file:
            flash("Product image is required.", "warning")
            return redirect(url_for("admin_products"))

        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        else:
            flash("Invalid file format for image.", "warning")
            return redirect(url_for("admin_products"))

        product = Product(
            name=name, price=price, image=image_path, description=description
        )
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully.", "success")
        return redirect(url_for("admin_products"))

    return render_template("admin/products.html", products=products)


@app.route("/admin-product/<int:product_id>", methods=["GET", "POST"])
def admin_product_details(product_id):
    if not is_admin():
        flash("You are not authorized to access admin page.", "warning")
        return redirect(url_for("login"))
    if not is_authenticated():
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))

    product = Product.query.filter_by(id=product_id).first()

    return render_template("admin/product-details.html", product=product)


@app.route("/delete-product/", methods=["GET", "POST"])
def delete_product():
    if not is_admin():
        flash("You are not authorized to access admin page.", "warning")
        return redirect(url_for("login"))
    status = is_authenticated()
    if not status:
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        product_id = request.form.get("product_id")
        product = Product.query.filter_by(id=product_id).first()
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully.", "success")

    return redirect(url_for("admin_products"))


@app.route("/admin-orders", methods=["GET", "POST"])
def admin_orders():
    if not is_admin():
        flash("You are not authorized to access admin page.", "warning")
        return redirect(url_for("login"))
    if not is_authenticated():
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))

    orders = OrderDetails.query.all()

    return render_template("admin/orders.html", orders=orders)


@app.route("/admin-orders/<int:order_id>", methods=["GET", "POST"])
def admin_order_details(order_id):
    if not is_admin():
        flash("You are not authorized to access admin page.", "warning")
        return redirect(url_for("login"))
    if not is_authenticated():
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))

    if request.method == "POST":
        order_status = request.form.get("order_status")
        od = OrderDetails.query.filter_by(id=order_id).first()
        od.status = order_status
        db.session.commit()
        flash("Order status updated successfully.", "success")
        return redirect(url_for("admin_orders"))

    order = OrderDetails.query.filter_by(id=order_id).first()
    return render_template("admin/order-details.html", order=order)


@app.route("/admin-customers", methods=["GET", "POST"])
def admin_customers():
    if not is_admin():
        flash("You are not authorized to access admin page.", "warning")
        return redirect(url_for("login"))
    if not is_authenticated():
        flash("Please login to continue.", "warning")
        return redirect(url_for("login"))
    return render_template("admin/customers.html")
