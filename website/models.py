from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import Email
from datetime import datetime, timezone


db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Ensures password is hashed
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Verifies password
    def check_password(self, password):
        return check_password_hash(self.password, password)


# Note Model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())  # Automatically updated when modified
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# Contact Model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)  # Email must be unique
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=func.now())

    # Custom email validation method (if needed, use it in forms or controllers)
    def validate_email(self):
        if not Email()(self.email):
            raise ValueError('Invalid email format')

    # Constructor for Contact (you may choose to move email validation to form-level)
    def __init__(self, name, email, message):
        self.name = name
        self.email = email
        self.message = message
        self.validate_email()




class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

    __table_args__ = (db.UniqueConstraint('city', 'region', 'location', name='unique_location'),)

    def __init__(self, city, region, location, timestamp=None):
        self.city = city
        self.region = region
        self.location = location
        self.timestamp = timestamp or datetime.now(timezone.utc)

