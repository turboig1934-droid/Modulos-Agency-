from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.models.contact import ContactMessage

@admin_bp.route('/messages')
@login_required
def messages():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    all_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/messages.html', messages=all_messages)

# ===== GET SINGLE MESSAGE DETAILS (Full Read) =====
@admin_bp.route('/messages/<int:id>')
@login_required
def get_message(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    msg = ContactMessage.query.get_or_404(id)
    
    # Auto-mark as read when viewed
    if not msg.is_read:
        msg.is_read = True
        db.session.commit()
    
    return jsonify({
        'id': msg.id,
        'name': msg.name,
        'email': msg.email,
        'subject': msg.subject or 'No Subject',
        'message': msg.message,
        'is_read': msg.is_read,
        'created_at': msg.created_at.strftime('%d/%m/%Y %H:%M')
    })

# ===== MARK SINGLE MESSAGE AS READ =====
@admin_bp.route('/messages/<int:id>/read', methods=['POST'])
@login_required
def mark_read(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    msg = ContactMessage.query.get_or_404(id)
    msg.is_read = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Marked as read'})

# ===== DELETE SINGLE MESSAGE =====
@admin_bp.route('/messages/<int:id>/delete', methods=['POST'])
@login_required
def delete_message(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    msg = ContactMessage.query.get_or_404(id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Message deleted'})

# ===== DELETE ALL MESSAGES =====
@admin_bp.route('/messages/delete-all', methods=['POST'])
@login_required
def delete_all_messages():
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    count = ContactMessage.query.count()
    ContactMessage.query.delete()
    db.session.commit()
    return jsonify({'success': True, 'count': count, 'message': f'{count} messages deleted'})

# ===== MARK ALL MESSAGES AS READ =====
@admin_bp.route('/messages/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    unread_count = ContactMessage.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True, 'count': unread_count, 'message': f'{unread_count} messages marked as read'})

# ===== GET UNREAD COUNT (For Badge) =====
@admin_bp.route('/messages/unread-count')
@login_required
def unread_count():
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    count = ContactMessage.query.filter_by(is_read=False).count()
    return jsonify({'unread_count': count})