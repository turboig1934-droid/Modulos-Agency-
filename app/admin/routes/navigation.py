from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.models.navigation import NavItem

@admin_bp.route('/navigation')
@login_required
def navigation():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    nav_items = NavItem.query.order_by(NavItem.order).all()
    return render_template('admin/navigation.html', nav_items=nav_items)

@admin_bp.route('/navigation/add', methods=['POST'])
@login_required
def add_nav_item():
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    title = request.form.get('title')
    url = request.form.get('url')
    icon = request.form.get('icon')
    order = NavItem.query.count() + 1
    
    nav = NavItem(title=title, url=url, icon=icon, order=order)
    db.session.add(nav)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/navigation/<int:id>/edit', methods=['POST'])
@login_required
def edit_nav_item(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    nav = NavItem.query.get_or_404(id)
    nav.title = request.form.get('title')
    nav.url = request.form.get('url')
    nav.icon = request.form.get('icon')
    nav.is_active = request.form.get('is_active') == 'on'
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/navigation/<int:id>/delete', methods=['POST'])
@login_required
def delete_nav_item(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    nav = NavItem.query.get_or_404(id)
    db.session.delete(nav)
    db.session.commit()
    return jsonify({'success': True})

@admin_bp.route('/navigation/reorder', methods=['POST'])
@login_required
def reorder_nav():
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    for item in data:
        nav = NavItem.query.get(item['id'])
        if nav:
            nav.order = item['order']
    db.session.commit()
    return jsonify({'success': True})