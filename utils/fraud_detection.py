# Extracts device info
def detect_fraud(amount, location):
    """Simple rule-based fraud detection"""
    suspicious_locations = ["North Korea", "Unknown"]
    fraud_threshold = 10000  # Example: Flag transactions > $10,000

    if amount > fraud_threshold or location in suspicious_locations:
        return True
    return False
