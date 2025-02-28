from flask import Flask
from models import db
from models.transaction import Transaction
from models.user import User
from config import Config
from datetime import datetime, timedelta, timezone
import random

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_sample_data():
    """Create sample transaction data for training"""
    with app.app_context():
        # Clear existing data
        Transaction.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create sample users
        users = []
        for i in range(3):
            user = User(
                username=f'user{i+1}',
                userid=f'user{i+1}',
                email=f'user{i+1}@example.com',
                phone=f'+1555000{i+1:04d}'
            )
            users.append(user)
        
        db.session.bulk_save_objects(users)
        db.session.commit()
        
        # Get user IDs
        user_ids = [user.userid for user in users]
        locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami']
        devices = ['device1', 'device2', 'device3', 'device4']
        
        # Generate normal transactions
        transactions = []
        base_time = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Normal transactions for each user
        for userid in user_ids:
            # Generate 50 normal transactions per user
            for i in range(50):
                amount = random.uniform(10, 1000)
                timestamp = base_time + timedelta(
                    days=random.randint(0, 29),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                transaction = Transaction(
                    userid=userid,
                    amount=amount,
                    location=random.choice(locations),
                    device_id=random.choice(devices),
                    timestamp=timestamp,
                    is_fraudulent=False,
                    is_approved=True,
                    approval_timestamp=timestamp + timedelta(minutes=1),
                    approval_notes="Automatic approval"
                )
                transactions.append(transaction)
        
        # Generate fraudulent transactions
        # 1. High amount transactions
        for userid in user_ids:
            timestamp = base_time + timedelta(days=random.randint(0, 29))
            transaction = Transaction(
                userid=userid,
                amount=random.uniform(5000, 10000),
                location=random.choice(locations),
                device_id=random.choice(devices),
                timestamp=timestamp,
                is_fraudulent=True,
                is_approved=False,
                approval_notes="High amount transaction"
            )
            transactions.append(transaction)
        
        # 2. Rapid location changes
        for userid in user_ids:
            base = base_time + timedelta(days=random.randint(0, 29))
            for i in range(3):
                transaction = Transaction(
                    userid=userid,
                    amount=random.uniform(100, 500),
                    location=locations[i],
                    device_id=random.choice(devices),
                    timestamp=base + timedelta(minutes=i*5),
                    is_fraudulent=True,
                    is_approved=False,
                    approval_notes="Suspicious location pattern"
                )
                transactions.append(transaction)
        
        # 3. Multiple declined transactions
        for userid in user_ids:
            base = base_time + timedelta(days=random.randint(0, 29))
            for i in range(4):
                transaction = Transaction(
                    userid=userid,
                    amount=random.uniform(1000, 2000),
                    location=random.choice(locations),
                    device_id=random.choice(devices),
                    timestamp=base + timedelta(minutes=i*10),
                    is_fraudulent=True,
                    is_approved=False,
                    is_declined=True,
                    approval_notes="Multiple declined attempts"
                )
                transactions.append(transaction)
        
        # Add all transactions to database
        db.session.bulk_save_objects(transactions)
        db.session.commit()
        
        print(f"Created {len(users)} sample users")
        print(f"Created {len(transactions)} sample transactions")
        print(f"Normal transactions: {sum(1 for t in transactions if not t.is_fraudulent)}")
        print(f"Fraudulent transactions: {sum(1 for t in transactions if t.is_fraudulent)}")

if __name__ == "__main__":
    create_sample_data() 