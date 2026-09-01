from app import db
from datetime import datetime
import enum
import secrets

class OrderStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'

class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class Order(db.Model):
    __tablename__ = 'orders'
    
    # ===== BASIC INFO =====
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    
    # ===== ORDER DETAILS =====
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    final_amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    
    # ===== STATUS =====
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # ===== DELIVERY =====
    delivery_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    
    # ===== ADDITIONAL INFO =====
    notes = db.Column(db.Text)
    requirements = db.Column(db.Text)
    custom_details = db.Column(db.Text)  # JSON string for custom fields
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ===== RELATIONSHIPS =====
    payments = db.relationship('Payment', backref='order', lazy=True, cascade='all, delete-orphan')
    
    # ===== METHODS =====
    
    @staticmethod
    def generate_order_number():
        """Generate unique order number"""
        return f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
    
    def calculate_total(self):
        """Calculate total amount"""
        self.total_amount = self.unit_price * self.quantity
        self.final_amount = self.total_amount - self.discount_amount + self.tax_amount
        return self.final_amount
    
    def is_paid(self):
        """Check if order is paid"""
        return self.payment_status == PaymentStatus.PAID
    
    def is_completed(self):
        """Check if order is completed"""
        return self.status == OrderStatus.COMPLETED
    
    def can_cancel(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]
    
    def cancel(self, reason=None):
        """Cancel order"""
        if self.can_cancel():
            self.status = OrderStatus.CANCELLED
            if reason:
                self.cancellation_reason = reason
            db.session.commit()
            return True
        return False
    
    def complete(self):
        """Mark order as completed"""
        if self.status == OrderStatus.PROCESSING:
            self.status = OrderStatus.COMPLETED
            self.completed_date = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        """Convert order to dictionary"""
        return {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'quantity': self.quantity,
            'total_amount': self.total_amount,
            'discount_amount': self.discount_amount,
            'tax_amount': self.tax_amount,
            'final_amount': self.final_amount,
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'payment_status': self.payment_status.value if self.payment_status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None
        }
    
    def __repr__(self):
        return f'<Order {self.order_number}>'