# Enhanced fraud detection logic
from models.transaction import Transaction
import json
from datetime import datetime

def detect_fraud(amount, location, userid):
    """
    Enhanced fraud detection with multiple rules
    
    Rules:
    1. Amount thresholds (existing)
    2. Amount 5x higher than user average
    3. Multiple locations within minutes
    4. Three declined transactions within 30 minutes
    """
    flags = []
    is_fraudulent = False
    
    # Rule 1: Basic amount thresholds
    SUSPICIOUS_AMOUNT = 10000.0
    HIGH_RISK_AMOUNT = 100000.0
    
    if amount >= HIGH_RISK_AMOUNT:
        flags.append(f"Amount ${amount:,.2f} exceeds high-risk threshold ${HIGH_RISK_AMOUNT:,.2f}")
        is_fraudulent = True
    elif amount >= SUSPICIOUS_AMOUNT:
        flags.append(f"Amount ${amount:,.2f} exceeds suspicious threshold ${SUSPICIOUS_AMOUNT:,.2f}")
        is_fraudulent = True
        
    # Rule 2: Check if amount is 5x higher than user's average
    avg_amount = Transaction.get_average_amount(userid)
    if avg_amount > 0 and amount > (avg_amount * 5):
        flags.append(f"Amount ${amount:,.2f} is more than 5x user's average (${avg_amount:,.2f})")
        is_fraudulent = True
    
    # Rule 3: Check for multiple locations within 5 minutes
    recent_transactions = Transaction.get_user_recent_transactions(userid, minutes=5)
    recent_locations = {t.location for t in recent_transactions if t.location != location}
    if recent_locations:
        flags.append(f"Multiple locations detected within 5 minutes: {location} and {', '.join(recent_locations)}")
        is_fraudulent = True
    
    # Rule 4: Check for three declined transactions
    declined_count = Transaction.get_user_declined_count(userid, minutes=30)
    if declined_count >= 3:
        flags.append(f"Card declined {declined_count} times in the last 30 minutes")
        is_fraudulent = True
    
    # Location-based check (existing)
    suspicious_locations = ["North Korea", "Unknown", "Restricted"]
    if location in suspicious_locations:
        flags.append(f"Suspicious location detected: {location}")
        is_fraudulent = True
    
    return is_fraudulent, json.dumps(flags) if flags else None
