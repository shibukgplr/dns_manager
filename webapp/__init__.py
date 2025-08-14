from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()

def create_app(config_class=Config):
    """
    Application factory function
    """
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register blueprints
    from webapp.routes import main as main_blueprint
    from webapp.auth import auth as auth_blueprint
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Import models and forms to ensure they're registered
    from webapp import models, forms

    return app

__all__ = ['create_app', 'db']
__version__ = '1.0.0'