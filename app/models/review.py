from app import db
from datetime import datetime
import json

class Review(db.Model):
    __tablename__ = 'reviews'
    
    # ===== BASIC INFO =====
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    
    # ===== REVIEW DETAILS =====
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(100))
    comment = db.Column(db.Text)
    
    # ===== STATUS =====
    is_verified = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    
    # ===== MEDIA =====
    images = db.Column(db.Text)  # JSON array of image URLs
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    
    # ===== METHODS =====
    
    def approve(self):
        self.is_approved = True
        self.approved_at = datetime.utcnow()
        db.session.commit()
        # Update service rating
        from app.models.service import Service
        service = Service.query.get(self.service_id)
        if service:
            service.update_rating()
    
    def reject(self):
        self.is_approved = False
        db.session.commit()
    
    def get_images_list(self):
        if self.images:
            try:
                return json.loads(self.images)
            except:
                return []
        return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'is_verified': self.is_verified,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }
    
    def __repr__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'