from app import db
from datetime import datetime

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False) # Increased to 120 (Standard for emails)
    subject = db.Column(db.String(200), nullable=True) # Added to match our form
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        # Updated repr to make admin debugging easier
        return f'<ContactMessage: {self.name} - {self.subject}>'