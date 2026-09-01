from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.contact import ContactMessage

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/services')
def services():
    return render_template('services.html')


@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    # Jab user Contact Us form submit kare (POST Request)
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic Validation
        if not name or not email or not message:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('main.contact'))

        # Database me Message Save karna (Taki Admin Panel par dikhe)
        try:
            new_msg = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            db.session.add(new_msg)
            db.session.commit()
            flash('Thank you for contacting us! We will get back to you soon.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Something went wrong while submitting your message. Please try again.', 'danger')

        return redirect(url_for('main.contact'))

    # Normal Page Load (GET Request)
    return render_template('contact.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


@main_bp.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'Modulos Agency'
    })