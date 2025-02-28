from flask import Flask
from models import db
from utils.fraud_detection import detect_fraud
from config import Config
from datetime import datetime, timedelta, timezone
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def test_fraud_detection():
    """Test various fraud detection scenarios"""
    with app.app_context():
        print("Testing Fraud Detection Scenarios\n")
        
        # Test Case 1: Normal Transaction
        print("Scenario 1: Normal Transaction")
        amount = 500.00
        location = "New York"
        userid = "user1"
        is_fraudulent, flags = detect_fraud(amount, location, userid)
        print(f"Amount: ${amount:,.2f}")
        print(f"Location: {location}")
        print(f"Result: {'Fraudulent' if is_fraudulent else 'Legitimate'}")
        print(f"Flags: {json.loads(flags)}\n")
        
        # Test Case 2: High Amount Transaction
        print("Scenario 2: High Amount Transaction")
        amount = 15000.00
        location = "Los Angeles"
        userid = "user1"
        is_fraudulent, flags = detect_fraud(amount, location, userid)
        print(f"Amount: ${amount:,.2f}")
        print(f"Location: {location}")
        print(f"Result: {'Fraudulent' if is_fraudulent else 'Legitimate'}")
        print(f"Flags: {json.loads(flags)}\n")
        
        # Test Case 3: Rapid Location Change
        print("Scenario 3: Rapid Location Change")
        amount = 300.00
        location = "Miami"  # Different from recent transactions
        userid = "user2"
        is_fraudulent, flags = detect_fraud(amount, location, userid)
        print(f"Amount: ${amount:,.2f}")
        print(f"Location: {location}")
        print(f"Result: {'Fraudulent' if is_fraudulent else 'Legitimate'}")
        print(f"Flags: {json.loads(flags)}\n")
        
        # Test Case 4: Amount Anomaly (5x user average)
        print("Scenario 4: Amount Anomaly")
        amount = 4500.00  # Should be much higher than user's average
        location = "Chicago"
        userid = "user3"
        is_fraudulent, flags = detect_fraud(amount, location, userid)
        print(f"Amount: ${amount:,.2f}")
        print(f"Location: {location}")
        print(f"Result: {'Fraudulent' if is_fraudulent else 'Legitimate'}")
        print(f"Flags: {json.loads(flags)}\n")
        
        # Test Case 5: Suspicious Location
        print("Scenario 5: Suspicious Location")
        amount = 750.00
        location = "High Risk Region"
        userid = "user1"
        is_fraudulent, flags = detect_fraud(amount, location, userid)
        print(f"Amount: ${amount:,.2f}")
        print(f"Location: {location}")
        print(f"Result: {'Fraudulent' if is_fraudulent else 'Legitimate'}")
        print(f"Flags: {json.loads(flags)}")

if __name__ == "__main__":
    test_fraud_detection() 