from app import db
from datetime import datetime, timedelta

class Ad(db.Model):
    __tablename__ = 'ads'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    click_url = db.Column(db.String(500), nullable=False)
    ad_type = db.Column(db.String(20), default='image')
    ad_size = db.Column(db.String(50), default='728x90')  # 160x600, 336x280, 970x250, 728x90, 300x250
    placement = db.Column(db.String(50), default='banner')  # banner, sidebar, billboard, popup
    is_active = db.Column(db.Boolean, default=True)
    is_popup = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    views = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    
    def is_expired(self):
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def is_visible(self):
        return self.is_active and not self.is_expired()
    
    def get_size_style(self):
        sizes = {
            '160x600': {'width': '160px', 'height': '600px', 'class': 'skyscraper'},
            '336x280': {'width': '336px', 'height': '280px', 'class': 'rectangle'},
            '970x250': {'width': '970px', 'height': '250px', 'class': 'billboard'},
            '728x90': {'width': '728px', 'height': '90px', 'class': 'leaderboard'},
            '300x250': {'width': '300px', 'height': '250px', 'class': 'medium'}
        }
        return sizes.get(self.ad_size, {'width': '300px', 'height': '250px', 'class': 'medium'})
    
    def get_size_class(self):
        sizes = {
            '160x600': 'ad-skyscraper',
            '336x280': 'ad-rectangle',
            '970x250': 'ad-billboard',
            '728x90': 'ad-leaderboard',
            '300x250': 'ad-medium'
        }
        return sizes.get(self.ad_size, 'ad-medium')
    
    def record_click(self):
        self.clicks += 1
        db.session.commit()
    
    def record_view(self):
        self.views += 1
        db.session.commit()
    
    def __repr__(self):
        return f'<Ad {self.title}>'