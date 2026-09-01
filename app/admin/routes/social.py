from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.admin import admin_bp
from app.models.social import SocialLink

# ===== PLATFORM TO ICON MAPPING =====
PLATFORM_ICONS = {
    'Discord': 'fab fa-discord',
    'Twitch': 'fab fa-twitch',
    'YouTube': 'fab fa-youtube',
    'Twitter': 'fab fa-twitter',
    'Instagram': 'fab fa-instagram',
    'Facebook': 'fab fa-facebook',
    'TikTok': 'fab fa-tiktok',
    'Snapchat': 'fab fa-snapchat',
    'Pinterest': 'fab fa-pinterest',
    'Threads': 'fas fa-threads',
    'Bluesky': 'fas fa-cloud-sun',
    'Mastodon': 'fab fa-mastodon',
    'Reddit': 'fab fa-reddit',
    'Tumblr': 'fab fa-tumblr',
    'WhatsApp': 'fab fa-whatsapp',
    'Telegram': 'fab fa-telegram',
    'Signal': 'fas fa-signal',
    'LinkedIn': 'fab fa-linkedin',
    'GitHub': 'fab fa-github',
    'GitLab': 'fab fa-gitlab',
    'Bitbucket': 'fab fa-bitbucket',
    'Stack Overflow': 'fab fa-stack-overflow',
    'HackerRank': 'fab fa-hackerrank',
    'LeetCode': 'fas fa-code',
    'Behance': 'fab fa-behance',
    'Dribbble': 'fab fa-dribbble',
    'Figma': 'fab fa-figma',
    'CodePen': 'fab fa-codepen',
    'DeviantArt': 'fab fa-deviantart',
    'Flickr': 'fab fa-flickr',
    'Medium': 'fab fa-medium',
    'Substack': 'fas fa-substack',
    'Quora': 'fab fa-quora',
    'Spotify': 'fab fa-spotify',
    'Vimeo': 'fab fa-vimeo',
    'Patreon': 'fab fa-patreon',
    'Website': 'fas fa-globe',
    'Linktree': 'fas fa-link',
}

@admin_bp.route('/social')
@login_required
def social():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    links = SocialLink.query.order_by(SocialLink.order).all()
    return render_template('admin/social.html', links=links)

@admin_bp.route('/social/add', methods=['POST'])
@login_required
def add_social():
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    platform = request.form.get('platform')
    url = request.form.get('url')
    
    if not platform or not url:
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.social'))
    
    icon = PLATFORM_ICONS.get(platform, 'fas fa-link')
    order = SocialLink.query.count() + 1
    
    link = SocialLink(name=platform, icon=icon, url=url, order=order)
    db.session.add(link)
    db.session.commit()
    flash(f'✅ {platform} link added successfully!', 'success')
    return redirect(url_for('admin.social'))

@admin_bp.route('/social/<int:id>/edit', methods=['GET'])
@login_required
def edit_social(id):
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    link = SocialLink.query.get_or_404(id)
    return render_template('admin/edit_social.html', link=link)

@admin_bp.route('/social/<int:id>/update', methods=['POST'])
@login_required
def update_social(id):
    if not current_user.is_admin():
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    link = SocialLink.query.get_or_404(id)
    platform = request.form.get('platform')
    url = request.form.get('url')
    
    if not platform or not url:
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin.social'))
    
    link.name = platform
    link.url = url
    link.icon = PLATFORM_ICONS.get(platform, 'fas fa-link')
    link.is_active = request.form.get('is_active') == 'on'
    db.session.commit()
    
    flash('✅ Social link updated successfully!', 'success')
    return redirect(url_for('admin.social'))

@admin_bp.route('/social/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_social(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    link = SocialLink.query.get_or_404(id)
    link.is_active = not link.is_active
    db.session.commit()
    return jsonify({'success': True, 'active': link.is_active})

@admin_bp.route('/social/<int:id>/delete', methods=['POST'])
@login_required
def delete_social(id):
    if not current_user.is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    link = SocialLink.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    return jsonify({'success': True})