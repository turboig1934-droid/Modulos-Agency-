from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.models.ad import Ad
from datetime import datetime, timedelta

@admin_bp.route('/ads')
@login_required
def ads():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    all_ads = Ad.query.order_by(Ad.created_at.desc()).all()
    return render_template('admin/ads.html', ads=all_ads)

@admin_bp.route('/ads/add', methods=['GET', 'POST'])
@login_required
def add_ad():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        image_url = request.form.get('image_url')
        click_url = request.form.get('click_url')
        ad_size = request.form.get('ad_size', '728x90')
        placement = request.form.get('placement', 'banner')
        is_popup = request.form.get('is_popup') == 'on'
        hours = int(request.form.get('hours', 24))
        
        if not title or not image_url or not click_url:
            flash('All fields are required.', 'danger')
            return render_template('admin/add_ad.html')
        
        ad = Ad(
            title=title,
            image_url=image_url,
            click_url=click_url,
            ad_size=ad_size,
            placement=placement,
            is_popup=is_popup,
            expires_at=datetime.utcnow() + timedelta(hours=hours)
        )
        db.session.add(ad)
        db.session.commit()
        flash(f'✅ Ad "{title}" added successfully!', 'success')
        return redirect(url_for('admin.ads'))
    
    return render_template('admin/add_ad.html')

@admin_bp.route('/ads/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_ad(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    ad = Ad.query.get_or_404(id)
    ad.is_active = not ad.is_active
    db.session.commit()
    return jsonify({'success': True, 'active': ad.is_active})

@admin_bp.route('/ads/<int:id>/delete', methods=['POST'])
@login_required
def delete_ad(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    ad = Ad.query.get_or_404(id)
    db.session.delete(ad)
    db.session.commit()
    return jsonify({'success': True})