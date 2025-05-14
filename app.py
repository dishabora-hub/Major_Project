from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import (
    LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user
)
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Length, EqualTo, Email
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime, timezone
import subprocess
import os

app = Flask(__name__)

# ————— Database Configuration —————
db_path = os.path.join(app.root_path, 'instance', 'user.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ————— Login Manager —————
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ————— Models —————
class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Contact(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(150), nullable=False)
    email   = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)

class Location(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    city      = db.Column(db.String(100), nullable=False)
    region    = db.Column(db.String(100), nullable=False)
    location  = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ————— Admin Panel —————
admin = Admin(app, name='Database Admin', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Contact, db.session))
admin.add_view(ModelView(Location, db.session))

# ————— Forms —————
class SignUpForm(FlaskForm):
    email            = StringField('Email', validators=[InputRequired(), Email(), Length(3,100)])
    password         = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])

class LoginForm(FlaskForm):
    email    = StringField('Email', validators=[InputRequired(), Email(), Length(3,100)])
    password = PasswordField('Password', validators=[InputRequired()])

class ContactForm(FlaskForm):
    name    = StringField('Name', validators=[InputRequired(), Length(2,100)])
    email   = StringField('Email', validators=[InputRequired(), Email(), Length(3,100)])
    message = TextAreaField('Message', validators=[InputRequired(), Length(10,500)])

# ————— Routes —————
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/contact', methods=['GET','POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Contact(name=form.name.data, email=form.email.data, message=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash("Your message has been sent!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists!", "danger")
        else:
            user = User(
                email=form.email.data,
                password=generate_password_hash(form.password.data, 'sha256')
            )
            db.session.add(user)
            db.session.commit()
            flash("Account created!", "success")
            return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('login.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/save_location', methods=['POST'])
def save_location():
    data = request.get_json()
    if 'error' in data:
        return jsonify(message=f"Error: {data['error']}"), 400
    try:
        ts = data.get('timestamp')
        if isinstance(ts, str):
            ts = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        else:
            ts = datetime.now(timezone.utc)

        loc = Location(
            city=data['city'],
            region=data['region'],
            location=data['location'],
            timestamp=ts
        )
        db.session.add(loc)
        db.session.commit()
        return jsonify(message="Location saved successfully"), 200

    except Exception as e:
        return jsonify(message=f"Failed to save location: {e}"), 500

@app.route('/location')
def location():
    history = Location.query.order_by(Location.timestamp.desc()).all()
    return render_template('location.html', locations=history)

@app.route('/run_model')
@login_required
def run_model():
    try:
        subprocess.Popen(["python", "fire_detection_alert_system.py"])
        flash("🔥 Fire detection started!", "success")
    except Exception as e:
        flash(f"Error starting detection: {e}", "danger")
    return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('login'))

# ————— Main —————
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
