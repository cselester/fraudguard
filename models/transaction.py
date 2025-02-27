# Transaction model
from models import db  # Import db from models/__init__.py
from datetime import datetime, timezone, timedelta
import secrets

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(50), db.ForeignKey('user.userid'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    device_id = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    is_fraudulent = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_declined = db.Column(db.Boolean, default=False)
    approval_timestamp = db.Column(db.DateTime, nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)
    fraud_flags = db.Column(db.Text, nullable=True)  # Store reasons for flagging
    approval_token = db.Column(db.String(100), unique=True, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Transaction {self.id}: ${self.amount} by {self.userid}>'

    def generate_approval_token(self):
        """Generate a unique token for transaction approval"""
        self.approval_token = secrets.token_urlsafe(32)
        self.token_expiry = datetime.now(timezone.utc) + timedelta(hours=24)
        return self.approval_token

    @classmethod
    def get_user_recent_transactions(cls, userid, minutes=5):
        """Get user's transactions in the last X minutes"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return cls.query.filter(
            cls.userid == userid,
            cls.timestamp >= cutoff_time
        ).order_by(cls.timestamp.desc()).all()

    @classmethod
    def get_user_declined_count(cls, userid, minutes=30):
        """Get count of user's declined transactions in last X minutes"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        return cls.query.filter(
            cls.userid == userid,
            cls.is_declined == True,
            cls.timestamp >= cutoff_time
        ).count()

    @classmethod
    def get_average_amount(cls, userid):
        """Get user's average transaction amount"""
        result = db.session.query(db.func.avg(cls.amount)).filter(
            cls.userid == userid,
            cls.is_approved == True
        ).scalar()
        return result or 0.0

