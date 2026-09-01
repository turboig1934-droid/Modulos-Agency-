from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models.user import User
from app.models.contact import ContactMessage
from app.models.ad import Ad

@admin_bp.route('/')
@login_required
def dashboard():
    if not current_user.is_admin():
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('main.index'))
    
    total_users = User.query.count()
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    total_ads = Ad.query.count()
    active_ads = Ad.query.filter_by(is_active=True).count()
    
    # Recent data
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
        total_users=total_users,
        total_messages=total_messages,
        unread_messages=unread_messages,
        total_ads=total_ads,
        active_ads=active_ads,
        recent_users=recent_users,
        recent_messages=recent_messages
    )