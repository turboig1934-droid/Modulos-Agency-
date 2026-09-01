from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
import random

# ===== CREATE BLUEPRINT FIRST =====
main_bp = Blueprint('main', __name__)

# ===== HELPER FUNCTIONS =====
def get_social_links():
    """Get all active social links"""
    try:
        from app.models.social import SocialLink
        return SocialLink.query.filter_by(is_active=True).order_by(SocialLink.order).all()
    except:
        return []

def get_active_ad():
    """Get a random active ad for display (banner/rectangle/skyscraper)"""
    try:
        from app.models.ad import Ad
        active_ads = Ad.query.filter_by(is_active=True, is_popup=False).all()
        # Filter out expired ads
        valid_ads = [ad for ad in active_ads if not ad.is_expired()]
        if valid_ads:
            ad = random.choice(valid_ads)
            ad.record_view()
            return ad
        return None
    except:
        return None

def get_random_popup_ad():
    """Get random popup ad"""
    try:
        from app.models.ad import Ad
        ads = Ad.query.filter_by(is_active=True, is_popup=True).all()
        valid_ads = [ad for ad in ads if not ad.is_expired()]
        if valid_ads:
            ad = random.choice(valid_ads)
            ad.record_view()
            return ad
        return None
    except:
        return None

def get_ads_by_size(size='728x90'):
    """Get active ads by size"""
    try:
        from app.models.ad import Ad
        ads = Ad.query.filter_by(is_active=True, ad_size=size).all()
        valid_ads = [ad for ad in ads if not ad.is_expired()]
        return valid_ads
    except:
        return []

# ===== PUBLIC ROUTES =====
@main_bp.route('/')
def index():
    ad = get_active_ad()
    popup_ad = get_random_popup_ad()
    return render_template('index.html', 
        ad=ad, 
        popup_ad=popup_ad,
        social_links=get_social_links()
    )

@main_bp.route('/about')
def about():
    return render_template('about.html', social_links=get_social_links())

@main_bp.route('/services')
def services():
    return render_template('services.html', social_links=get_social_links())

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    from app.models.contact import ContactMessage
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject', '')
        message = request.form.get('message')
        
        if name and email and message:
            msg = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            db.session.add(msg)
            db.session.commit()
            flash('Thank you! We will get back to you soon.', 'success')
            return redirect(url_for('main.contact'))
        else:
            flash('Please fill in all required fields.', 'danger')
            return render_template('contact.html', social_links=get_social_links())
    
    return render_template('contact.html', social_links=get_social_links())

# ===== AD CLICK ROUTE =====
@main_bp.route('/ad-click/<int:ad_id>')
def ad_click(ad_id):
    from app.models.ad import Ad
    ad = Ad.query.get_or_404(ad_id)
    ad.record_click()
    return redirect(ad.click_url)

# ===== AD VIEW ROUTE (For popup tracking) =====
@main_bp.route('/ad-view/<int:ad_id>', methods=['POST'])
def ad_view(ad_id):
    from app.models.ad import Ad
    ad = Ad.query.get_or_404(ad_id)
    ad.record_view()
    return jsonify({'success': True})

# ===== USER DASHBOARD (Login Required) =====
@main_bp.route('/dashboard')
@login_required
def dashboard():
    ad = get_active_ad()
    popup_ad = get_random_popup_ad()
    return render_template('dashboard.html', 
        user=current_user, 
        ad=ad,
        popup_ad=popup_ad,
        social_links=get_social_links()
    )

# ===== API HEALTH CHECK =====
@main_bp.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Modulos Agency'})