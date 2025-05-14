from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignupForm, LoginForm  # Import the forms

auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()  # Create an instance of SignupForm

    if form.validate_on_submit():  # Validate the form
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email already exists.', category='error')
        else:
            new_user = User(email=form.email.data, password=generate_password_hash(form.password.data, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', category='success')
            return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)  # Pass form to template


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Create an instance of LoginForm

    if form.validate_on_submit():  # Validate form
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            flash('Logged in successfully!', category='success')
            return redirect(url_for('main.home'))  # Redirect to the home page
        else:
            flash('Incorrect email or password.', category='error')

    return render_template('login.html', form=form)  # Pass form to template
