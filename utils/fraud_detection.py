# Enhanced fraud detection logic
from models.transaction import Transaction
import json
from datetime import datetime, timedelta, timezone
from ml.random_forest_model import FraudDetectionModel
from models import db

# Initialize the model
model = FraudDetectionModel()
ML_MODEL_AVAILABLE = False
try:
    model.load_model()
    ML_MODEL_AVAILABLE = True
    print("ML model loaded successfully!")
except:
    print("No trained model found. Using rule-based detection only.")

def get_user_transaction_history(userid):
    """Get user's transaction history"""
    transactions = Transaction.query.filter_by(userid=userid).all()
    transaction_data = []
    
    for t in transactions:
        transaction_data.append({
            'userid': t.userid,
            'amount': float(t.amount),
            'location': t.location,
            'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'is_fraudulent': t.is_fraudulent,
            'device_id': t.device_id
        })
    
    return transaction_data

def apply_rule_based_detection(amount, location, userid, transaction_history, current_time):
    """Apply rule-based fraud detection"""
    fraud_flags = []
    
    # Rule 1: Basic amount thresholds
    SUSPICIOUS_AMOUNT = 10000.0
    HIGH_RISK_AMOUNT = 100000.0
    
    if amount >= HIGH_RISK_AMOUNT:
        fraud_flags.append(f"Amount ${amount:,.2f} exceeds high-risk threshold ${HIGH_RISK_AMOUNT:,.2f}")
    elif amount >= SUSPICIOUS_AMOUNT:
        fraud_flags.append(f"Amount ${amount:,.2f} exceeds suspicious threshold ${SUSPICIOUS_AMOUNT:,.2f}")
    
    if transaction_history:
        # Rule 2: Check for amount anomalies
        avg_amount = sum(t['amount'] for t in transaction_history) / len(transaction_history)
        if amount > avg_amount * 5:
            fraud_flags.append(f"Amount is 5x higher than user average (${avg_amount:.2f})")
        
        # Rule 3: Check for rapid location changes
        recent_transactions = [t for t in transaction_history 
                             if (current_time - datetime.strptime(t['timestamp'], '%Y-%m-%d %H:%M:%S')
                                 .replace(tzinfo=timezone.utc)).total_seconds() <= 300]
        
        if recent_transactions:
            unique_locations = {t['location'] for t in recent_transactions}
            if location not in unique_locations and len(unique_locations) >= 2:
                fraud_flags.append("Multiple transactions from different locations within 5 minutes")
        
        # Rule 4: Check for declined transactions
        recent_declined = Transaction.query.filter(
            Transaction.userid == userid,
            Transaction.is_declined == True,
            Transaction.timestamp >= current_time - timedelta(minutes=30)
        ).count()
        
        if recent_declined >= 3:
            fraud_flags.append(f"Card declined {recent_declined} times in last 30 minutes")
        
        # Rule 5: Check transaction frequency
        if len(recent_transactions) >= 3:
            fraud_flags.append(f"High transaction frequency: {len(recent_transactions)} transactions in 5 minutes")
    
    # Rule 6: Check for suspicious locations
    suspicious_locations = {'Unknown', 'Restricted', 'High Risk Region'}
    if location in suspicious_locations:
        fraud_flags.append(f"Transaction from suspicious location: {location}")
    
    return fraud_flags

def detect_fraud(amount, location, userid):
    """
    Hybrid fraud detection using both ML and rule-based approaches
    Returns: (is_fraudulent, fraud_flags)
    """
    fraud_flags = []
    current_time = datetime.now(timezone.utc)
    
    # Get user's transaction history
    transaction_history = get_user_transaction_history(userid)
    
    # Apply rule-based detection
    rule_based_flags = apply_rule_based_detection(amount, location, userid, transaction_history, current_time)
    fraud_flags.extend(rule_based_flags)
    
    # Apply ML-based detection if available
    if ML_MODEL_AVAILABLE:
        try:
            current_transaction = {
                'userid': userid,
                'amount': float(amount),
                'location': location,
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_fraudulent': False,
                'device_id': None
            }
            
            prediction = model.predict(current_transaction)
            if prediction['is_fraudulent']:
                fraud_flags.append(f"ML Model detected suspicious pattern (confidence: {prediction['confidence']:.1%})")
                
                # Add top contributing factors
                sorted_features = sorted(prediction['feature_importance'].items(), 
                                      key=lambda x: x[1], reverse=True)[:2]
                for feature, importance in sorted_features:
                    fraud_flags.append(f"High risk factor: {feature} (importance: {importance:.1%})")
        except Exception as e:
            print(f"ML prediction failed: {str(e)}")
            # Continue with rule-based results
    
    # Determine final fraud status
    is_fraudulent = len(fraud_flags) > 0
    
    # Add detection method to flags
    if fraud_flags:
        detection_methods = []
        if rule_based_flags:
            detection_methods.append("Rule-based")
        if ML_MODEL_AVAILABLE and prediction.get('is_fraudulent'):
            detection_methods.append("ML-based")
        fraud_flags.insert(0, f"Detection method(s): {' & '.join(detection_methods)}")
    
    return is_fraudulent, json.dumps(fraud_flags)
