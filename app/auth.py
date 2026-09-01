from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from datetime import datetime, timedelta
import random
import re
import secrets
from app import db, bcrypt, mail
from app.models.user import User

# ===== CREATE BLUEPRINT =====
auth_bp = Blueprint('auth', __name__)

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_otp():
    """Generate 4-digit OTP"""
    return str(random.randint(1000, 9999))

def send_otp_email(user, otp):
    """Send OTP via email"""
    try:
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8faff; padding: 40px; }}
                .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 20px; border: 1px solid #e6f0ff; }}
                .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #e6f0ff; }}
                .header h1 {{ color: #0a3b6b; font-size: 28px; margin: 0; }}
                .header span {{ color: #0070e0; }}
                .otp-box {{ text-align: center; padding: 30px 0; }}
                .otp-code {{ font-size: 48px; font-weight: 700; color: #0a3b6b; background: #f0f8ff; padding: 15px 30px; border-radius: 12px; letter-spacing: 10px; display: inline-block; border: 2px dashed #0070e0; }}
                .footer {{ text-align: center; color: #8a9bb5; font-size: 13px; padding-top: 20px; border-top: 1px solid #e6f0ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Modulos <span>Agency</span></h1>
                    <p>Build. Scale. Dominate.</p>
                </div>
                <div class="otp-box">
                    <p>Hello <strong>{user.full_name}</strong>,</p>
                    <p>Your verification code is:</p>
                    <div class="otp-code">{otp}</div>
                    <p style="color: #8a9bb5; font-size: 14px; margin-top: 15px;">Valid for 10 minutes</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 Modulos Agency. All rights reserved.</p>
                    <p>📧 modulosagency@gmail.com</p>
                </div>
            </div>
        </body>
        </html>
        '''
        msg = Message(
            subject='🔐 Verify Your Email - Modulos Agency',
            recipients=[user.email],
            html=html
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_reset_email(user, reset_url):
    """Send password reset email"""
    try:
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8faff; padding: 40px; }}
                .container {{ max-width: 500px; margin: 0 auto; background: white; padding: 40px; border-radius: 20px; border: 1px solid #e6f0ff; }}
                .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #e6f0ff; }}
                .header h1 {{ color: #0a3b6b; font-size: 28px; margin: 0; }}
                .header span {{ color: #0070e0; }}
                .btn {{ display: inline-block; background: #0a3b6b; color: white; padding: 14px 40px; border-radius: 30px; text-decoration: none; margin: 20px 0; }}
                .footer {{ text-align: center; color: #8a9bb5; font-size: 13px; padding-top: 20px; border-top: 1px solid #e6f0ff; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Modulos <span>Agency</span></h1>
                    <p>Build. Scale. Dominate.</p>
                </div>
                <div style="text-align: center; padding: 20px 0;">
                    <p>Hello <strong>{user.full_name}</strong>,</p>
                    <p>We received a request to reset your password.</p>
                    <a href="{reset_url}" class="btn">Reset Password</a>
                    <p style="color: #8a9bb5; font-size: 14px;">This link expires in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2026 Modulos Agency. All rights reserved.</p>
                    <p>📧 modulosagency@gmail.com</p>
                </div>
            </div>
        </body>
        </html>
        '''
        msg = Message(
            subject='🔑 Reset Your Password - Modulos Agency',
            recipients=[user.email],
            html=html
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Reset email error: {e}")
        return False

# ============================================
# REGISTER ROUTE
# ============================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/register.html')
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash('Username can only contain letters, numbers and underscore.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            password_hash=hashed_password,
            is_verified=False
        )
        db.session.add(user)
        db.session.commit()
        
        otp = generate_otp()
        user.otp_code = otp
        user.otp_created_at = datetime.utcnow()
        user.otp_attempts = 0
        db.session.commit()
        
        if send_otp_email(user, otp):
            flash('Registration successful! A verification code has been sent to your email.', 'success')
            session['verify_email'] = user.email
            return redirect(url_for('auth.verify_otp'))
        else:
            user.is_verified = True
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

# ============================================
# VERIFY OTP ROUTE
# ============================================

@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = session.get('verify_email')
    if not email:
        flash('Please register first.', 'warning')
        return redirect(url_for('auth.register'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('auth.register'))
    
    if user.is_verified:
        flash('Email already verified. Please login.', 'info')
        return redirect(url_for('auth.login'))
    
    # Hide middle letters of email
    email_parts = email.split('@')
    name = email_parts[0]
    if len(name) > 4:
        hidden_name = name[:2] + '***' + name[-2:]
    else:
        hidden_name = name[:1] + '***' + name[-1:]
    hidden_email = hidden_name + '@' + email_parts[1]
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        if not entered_otp:
            flash('Please enter the verification code.', 'danger')
            return render_template('auth/verify_otp.html', email=hidden_email)
        if user.otp_created_at and (datetime.utcnow() - user.otp_created_at).seconds > 600:
            flash('OTP has expired. Please request a new one.', 'danger')
            return render_template('auth/verify_otp.html', email=hidden_email)
        if user.otp_attempts >= 5:
            flash('Too many failed attempts. Please request a new OTP.', 'danger')
            return render_template('auth/verify_otp.html', email=hidden_email)
        if user.otp_code == entered_otp:
            user.is_verified = True
            user.otp_code = None
            user.otp_created_at = None
            user.otp_attempts = 0
            db.session.commit()
            session.pop('verify_email', None)
            flash('Email verified successfully! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            user.otp_attempts += 1
            db.session.commit()
            remaining = 5 - user.otp_attempts
            flash(f'Invalid OTP. {remaining} attempts remaining.', 'danger')
            return render_template('auth/verify_otp.html', email=hidden_email)
    
    return render_template('auth/verify_otp.html', email=hidden_email)

# ============================================
# RESEND OTP ROUTE
# ============================================

@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    email = session.get('verify_email')
    if not email:
        return jsonify({'success': False, 'message': 'No email found.'})
    
    user = User.query.filter_by(email=email).first()
    if not user or user.is_verified:
        return jsonify({'success': False, 'message': 'User already verified.'})
    
    otp = generate_otp()
    user.otp_code = otp
    user.otp_created_at = datetime.utcnow()
    user.otp_attempts = 0
    db.session.commit()
    
    if send_otp_email(user, otp):
        return jsonify({'success': True, 'message': 'New OTP sent to your email.'})
    else:
        return jsonify({'success': False, 'message': 'Failed to send email.'})

# ============================================
# LOGIN ROUTE
# ============================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_verified:
                session['verify_email'] = user.email
                flash('Please verify your email first. Check your inbox for OTP.', 'warning')
                return redirect(url_for('auth.verify_otp'))
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)
            session.permanent = True
            next_page = request.args.get('next')
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

# ============================================
# LOGOUT ROUTE
# ============================================

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

# ============================================
# FORGOT PASSWORD ROUTE
# ============================================

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('No account found with that email.', 'danger')
            return render_template('auth/forgot_password.html')
        
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        if send_reset_email(user, reset_url):
            flash('Password reset link has been sent to your email.', 'success')
        else:
            flash('Failed to send email. Please try again.', 'danger')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

# ============================================
# RESET PASSWORD ROUTE
# ============================================

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.query.filter_by(reset_token=token).first()
    
    if not user:
        flash('Invalid or expired reset link. Please try again.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if user.reset_token_expiry and datetime.utcnow() > user.reset_token_expiry:
        flash('Reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html')
        
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return render_template('auth/reset_password.html')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user.password_hash = hashed_password
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Password reset successfully! You can now login with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html')