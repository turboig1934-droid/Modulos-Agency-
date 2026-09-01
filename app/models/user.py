from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import enum

class UserRole(enum.Enum):
    USER = 'user'
    ADMIN = 'admin'
    SUPER_ADMIN = 'super_admin'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    # ===== BASIC INFO =====
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    
    # ===== PROFILE =====
    avatar = db.Column(db.String(255), default='default.png')
    bio = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # ===== EMAIL VERIFICATION (OTP) =====
    is_verified = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_created_at = db.Column(db.DateTime, nullable=True)
    otp_attempts = db.Column(db.Integer, default=0)
    
    # ===== PASSWORD RESET =====
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # ===== SECURITY =====
    is_active = db.Column(db.Boolean, default=True)
    is_blocked = db.Column(db.Boolean, default=False)
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    last_ip = db.Column(db.String(45), nullable=True)
    last_user_agent = db.Column(db.String(255), nullable=True)
    
    # ===== 2FA =====
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(255), nullable=True)
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)
    
    # ===== RELATIONSHIPS =====
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy=True, cascade='all, delete-orphan')
    payments = db.relationship('Payment', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # ===== METHODS =====
    
    def is_admin(self):
        """Check if user is admin or super admin"""
        return self.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    def is_super_admin(self):
        """Check if user is super admin"""
        return self.role == UserRole.SUPER_ADMIN
    
    def is_verified_user(self):
        """Check if user email is verified"""
        return self.is_verified
    
    def is_account_locked(self):
        """Check if account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def get_full_name(self):
        """Get user's full name"""
        return self.full_name
    
    def get_avatar_url(self):
        """Get user avatar URL"""
        return f"/static/uploads/avatars/{self.avatar}" if self.avatar else "/static/images/default-avatar.png"
    
    def increment_login_attempts(self):
        """Increment login attempts and lock if too many"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        db.session.commit()
    
    def reset_login_attempts(self):
        """Reset login attempts after successful login"""
        self.login_attempts = 0
        self.locked_until = None
        db.session.commit()
    
    def update_last_login(self, ip=None, user_agent=None):
        """Update last login info"""
        self.last_login = datetime.utcnow()
        if ip:
            self.last_ip = ip
        if user_agent:
            self.last_user_agent = user_agent
        db.session.commit()
    
    def generate_otp(self):
        """Generate and set OTP for email verification"""
        import random
        otp = str(random.randint(1000, 9999))
        self.otp_code = otp
        self.otp_created_at = datetime.utcnow()
        self.otp_attempts = 0
        db.session.commit()
        return otp
    
    def verify_otp(self, entered_otp):
        """Verify OTP and return boolean"""
        if not self.otp_code or not self.otp_created_at:
            return False
        
        # Check expiry (10 minutes)
        if (datetime.utcnow() - self.otp_created_at).seconds > 600:
            return False
        
        # Check attempts
        if self.otp_attempts >= 5:
            return False
        
        if self.otp_code == entered_otp:
            self.is_verified = True
            self.otp_code = None
            self.otp_created_at = None
            self.otp_attempts = 0
            db.session.commit()
            return True
        else:
            self.otp_attempts += 1
            db.session.commit()
            return False
    
    def soft_delete(self):
        """Soft delete user"""
        self.is_active = False
        self.deleted_at = datetime.utcnow()
        db.session.commit()
    
    def restore(self):
        """Restore soft deleted user"""
        self.is_active = True
        self.deleted_at = None
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value if self.role else None,
            'is_verified': self.is_verified,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.username}>'