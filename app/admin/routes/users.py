from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models.user import User

@admin_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    all_users = User.query.all()
    return render_template('admin/users.html', users=all_users)