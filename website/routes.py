from flask import Blueprint, render_template

main = Blueprint('main', __name__)  # ✅ Define Blueprint

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/about')
def about():
    return render_template('about.html')  # Ensure about.html exists in templates folder

@main.route('/faq')
def faq():
    return render_template('faq.html')  # Ensure faq.html exists

@main.route('/contact')
def contact():
    return render_template('contact.html')  # Ensure contact.html exists in templates

@main.route('/run_model', methods=['POST'])
def run_model():
    # Add your model loading and prediction code here
    return "Model ran successfully!"
