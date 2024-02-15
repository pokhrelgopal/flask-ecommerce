from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=True, default="user")
    _password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self._password, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Product %r>" % self.name
