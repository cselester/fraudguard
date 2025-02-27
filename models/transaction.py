# Transaction model
from models import db  # Import db from models/__init__.py
from datetime import datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    device_id = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_fraudulent = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    approval_timestamp = db.Column(db.DateTime, nullable=True)
    approval_notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Transaction {self.id}: ${self.amount} by {self.userid}>'

