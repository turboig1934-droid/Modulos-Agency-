from app import db
from datetime import datetime
import enum
import json

class ServiceCategory(enum.Enum):
    GAMING = 'gaming'
    YOUTUBE = 'youtube'
    BUSINESS = 'business'
    SOCIAL_MEDIA = 'social_media'

class ServiceStatus(enum.Enum):
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'

class Service(db.Model):
    __tablename__ = 'services'
    
    # ===== BASIC INFO =====
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    short_description = db.Column(db.String(200))
    category = db.Column(db.Enum(ServiceCategory), nullable=False)
    status = db.Column(db.Enum(ServiceStatus), default=ServiceStatus.DRAFT)
    
    # ===== PRICING =====
    price = db.Column(db.Float, nullable=False, default=0.0)
    price_type = db.Column(db.String(20), default='fixed')  # fixed, hourly, monthly, yearly
    discount_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='USD')
    
    # ===== FEATURES =====
    features = db.Column(db.Text)  # JSON string of features
    requirements = db.Column(db.Text)  # What client needs to provide
    deliverables = db.Column(db.Text)  # What client will receive
    timeline = db.Column(db.String(100))  # e.g., "3-5 business days"
    
    # ===== MEDIA =====
    image = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    gallery_images = db.Column(db.Text)  # JSON array of image URLs
    video_url = db.Column(db.String(255))
    
    # ===== SEO =====
    meta_title = db.Column(db.String(100))
    meta_description = db.Column(db.String(200))
    meta_keywords = db.Column(db.String(200))
    
    # ===== STATS =====
    views = db.Column(db.Integer, default=0)
    orders_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # ===== RELATIONSHIPS =====
    reviews = db.relationship('Review', backref='service', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='service', lazy=True, cascade='all, delete-orphan')
    
    # ===== METHODS =====
    
    def get_price_display(self):
        """Get formatted price with discount"""
        if self.discount_price and self.discount_price < self.price:
            return {
                'original': self.price,
                'discount': self.discount_price,
                'saved': self.price - self.discount_price,
                'currency': self.currency,
                'percentage': int(((self.price - self.discount_price) / self.price) * 100)
            }
        return {
            'original': self.price,
            'discount': None,
            'saved': 0,
            'currency': self.currency,
            'percentage': 0
        }
    
    def is_published(self):
        """Check if service is published"""
        return self.status == ServiceStatus.PUBLISHED
    
    def get_features_list(self):
        """Get features as list"""
        if self.features:
            try:
                return json.loads(self.features)
            except:
                return [f.strip() for f in self.features.split(',') if f.strip()]
        return []
    
    def get_gallery_images(self):
        """Get gallery images as list"""
        if self.gallery_images:
            try:
                return json.loads(self.gallery_images)
            except:
                return [self.gallery_images] if self.gallery_images else []
        return []
    
    def increment_views(self):
        """Increment view count"""
        self.views += 1
        db.session.commit()
    
    def update_rating(self):
        """Update average rating from approved reviews"""
        approved_reviews = [r for r in self.reviews if r.is_approved]
        if approved_reviews:
            total = sum(r.rating for r in approved_reviews)
            count = len(approved_reviews)
            self.rating = round(total / count, 1)
            self.rating_count = count
        else:
            self.rating = 0.0
            self.rating_count = 0
        db.session.commit()
    
    def publish(self):
        """Publish the service"""
        self.status = ServiceStatus.PUBLISHED
        self.published_at = datetime.utcnow()
        db.session.commit()
    
    def archive(self):
        """Archive the service"""
        self.status = ServiceStatus.ARCHIVED
        db.session.commit()
    
    def to_dict(self):
        """Convert service to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'short_description': self.short_description,
            'category': self.category.value if self.category else None,
            'status': self.status.value if self.status else None,
            'price': self.price,
            'discount_price': self.discount_price,
            'currency': self.currency,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'image': self.image,
            'icon': self.icon,
            'features': self.get_features_list(),
            'timeline': self.timeline,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None
        }
    
    def __repr__(self):
        return f'<Service {self.name}>'