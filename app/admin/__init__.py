from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.admin.routes import dashboard, messages, ads, users, navigation, settings, social

__all__ = ['admin_bp']