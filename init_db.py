from app import create_app, db
from app.models.user import User
from app.models.ad import Ad
from app.models.contact import ContactMessage
from app.models.social import SocialLink
from app.models.service import Service
from app.models.order import Order
from app.models.navigation import NavItem
from app.models.payment import Payment
from app.models.review import Review
from flask_bcrypt import Bcrypt

print("🔧 Initializing Database...")

app = create_app()

with app.app_context():
    print("📋 Dropping all tables...")
    db.drop_all()
    
    print("📋 Creating all tables...")
    db.create_all()
    
    print("✅ All tables created successfully!")
    
    # Create admin user
    from app.models.user import UserRole
    bcrypt = Bcrypt()
    
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
        print("✅ Admin created: admin@modulosagency.com / admin@123")
    else:
        print("✅ Admin already exists")
    
    # Check if ads table has columns
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('ads')]
    print(f"📋 Ads columns: {columns}")
    
    print("✅ Database initialization complete!")

print("🚀 Run 'py run.py' to start the server.")