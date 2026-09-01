from app import db
from datetime import datetime
import enum

class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class PaymentMethod(enum.Enum):
    STRIPE = 'stripe'
    PAYPAL = 'paypal'
    RAZORPAY = 'razorpay'

class Payment(db.Model):
    __tablename__ = 'payments'
    
    # ===== BASIC INFO =====
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    
    # ===== PAYMENT DETAILS =====
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = db.Column(db.Enum(PaymentMethod))
    
    # ===== TRANSACTION IDs =====
    transaction_id = db.Column(db.String(100))
    payment_intent_id = db.Column(db.String(100))
    
    # ===== PAYMENT DATA =====
    payment_data = db.Column(db.Text)  # JSON string for gateway response
    webhook_data = db.Column(db.Text)  # JSON string for webhook response
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # ===== METHODS =====
    
    def is_completed(self):
        return self.status == PaymentStatus.COMPLETED
    
    def complete(self):
        self.status = PaymentStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def fail(self):
        self.status = PaymentStatus.FAILED
        db.session.commit()
    
    def refund(self):
        self.status = PaymentStatus.REFUNDED
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status.value if self.status else None,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<Payment {self.transaction_id}>'