from flask import Flask
from models import db
from models.transaction import Transaction
from config import Config
from datetime import datetime, timedelta, timezone
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_sample_data():
    """Create sample transactions demonstrating different fraud scenarios"""
    with app.app_context():
        # Clear existing data
        Transaction.query.delete()
        db.session.commit()

        # Get current time in UTC
        now = datetime.now(timezone.utc)

        # Normal transactions for user1
        normal_transactions = [
            Transaction(
                userid="user1",
                amount=100.00,
                location="New York",
                device_id="device1",
                timestamp=now - timedelta(days=1),
                is_approved=True
            ),
            Transaction(
                userid="user1",
                amount=150.00,
                location="New York",
                device_id="device1",
                timestamp=now - timedelta(hours=12),
                is_approved=True
            )
        ]

        # Scenario 1: Amount 5x higher than average
        high_amount_transaction = Transaction(
            userid="user1",
            amount=1000.00,  # Much higher than previous average
            location="New York",
            device_id="device1",
            timestamp=now,
            is_fraudulent=True,
            fraud_flags=json.dumps(["Amount $1,000.00 is more than 5x user's average ($125.00)"])
        )

        # Scenario 2: Multiple locations within minutes
        multi_location_transactions = [
            Transaction(
                userid="user2",
                amount=200.00,
                location="Los Angeles",
                device_id="device2",
                timestamp=now - timedelta(minutes=2),
                is_fraudulent=True,
                fraud_flags=json.dumps(["Multiple locations detected within 5 minutes: Los Angeles and New York"])
            ),
            Transaction(
                userid="user2",
                amount=300.00,
                location="New York",
                device_id="device2",
                timestamp=now,
                is_fraudulent=True,
                fraud_flags=json.dumps(["Multiple locations detected within 5 minutes: New York and Los Angeles"])
            )
        ]

        # Scenario 3: Three declined transactions
        declined_transactions = [
            Transaction(
                userid="user3",
                amount=500.00,
                location="Chicago",
                device_id="device3",
                timestamp=now - timedelta(minutes=25),
                is_declined=True
            ),
            Transaction(
                userid="user3",
                amount=500.00,
                location="Chicago",
                device_id="device3",
                timestamp=now - timedelta(minutes=20),
                is_declined=True
            ),
            Transaction(
                userid="user3",
                amount=500.00,
                location="Chicago",
                device_id="device3",
                timestamp=now - timedelta(minutes=15),
                is_declined=True
            ),
            Transaction(
                userid="user3",
                amount=500.00,
                location="Chicago",
                device_id="device3",
                timestamp=now,
                is_fraudulent=True,
                fraud_flags=json.dumps(["Card declined 3 times in the last 30 minutes"])
            )
        ]

        # Scenario 4: High-risk amount
        high_risk_transaction = Transaction(
            userid="user4",
            amount=150000.00,
            location="Miami",
            device_id="device4",
            timestamp=now,
            is_fraudulent=True,
            fraud_flags=json.dumps(["Amount $150,000.00 exceeds high-risk threshold $100,000.00"])
        )

        # Scenario 5: Suspicious location
        suspicious_location_transaction = Transaction(
            userid="user5",
            amount=1000.00,
            location="Unknown",
            device_id="device5",
            timestamp=now,
            is_fraudulent=True,
            fraud_flags=json.dumps(["Suspicious location detected: Unknown"])
        )

        # Add all transactions
        all_transactions = (
            normal_transactions +
            [high_amount_transaction] +
            multi_location_transactions +
            declined_transactions +
            [high_risk_transaction, suspicious_location_transaction]
        )

        for transaction in all_transactions:
            db.session.add(transaction)

        db.session.commit()
        print(f"Created {len(all_transactions)} sample transactions")

if __name__ == "__main__":
    create_sample_data()