from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
from os import path, makedirs

db = SQLAlchemy()
migrate = Migrate()  # Initialize Migrate
DB_NAME = "users.db"




def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Define database path inside instance folder
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path.join(app.instance_path, DB_NAME)}'
    db.init_app(app)
    migrate.init_app(app, db)  # ✅ Correct way to initialize Migrate

    from .routes import main
    from .auth import auth

    app.register_blueprint(main, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)  # Ensure database exists

    return app

def create_database(app):
    with app.app_context():
        makedirs(app.instance_path, exist_ok=True)
        db.create_all()
        print("Database checked/created successfully!")
