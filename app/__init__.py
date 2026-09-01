from flask import Flask, render_template, session, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_mail import Mail
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///modulos.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Email Configuration (Gmail)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'modulosagency@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = 'Modulos Agency <modulosagency@gmail.com>'
    
    # Initialize
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login to access this page.'
    login_manager.login_message_category = 'warning'
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # Import models
    from app.models.user import User
    from app.models.contact import ContactMessage
    from app.models.ad import Ad
    from app.models.navigation import NavItem
    from app.models.social import SocialLink
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth import auth_bp
    from app.routes import main_bp
    from app.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # Create tables (without dropping)
    with app.app_context():
        # ONLY create tables if they don't exist - NO DATA LOSS
        db.create_all()
        
        # Create default admin user if not exists
        from app.models.user import UserRole
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@modulosagency.com',
                full_name='Admin',
                password_hash=bcrypt.generate_password_hash('admin@123').decode('utf-8'),
                role=UserRole.ADMIN,
                is_verified=True
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created: admin@modulosagency.com / admin@123")
        else:
            print("✅ Admin already exists - data preserved")
    
    return app

# Create app instance for run.py
app = create_app()