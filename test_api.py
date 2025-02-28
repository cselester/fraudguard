import requests
import json
from datetime import datetime

def test_fraud_detection_api():
    """Test the fraud detection API with various scenarios"""
    base_url = "http://127.0.0.1:5000"
    
    # Test scenarios
    scenarios = [
        {
            "name": "Normal Transaction",
            "data": {
                "userid": "user1",
                "amount": 500.00,
                "device_id": "device1"  # Optional, will be auto-detected
            }
        },
        {
            "name": "High Amount Transaction",
            "data": {
                "userid": "user1",
                "amount": 15000.00,
                "device_id": "device1"
            }
        },
        {
            "name": "Rapid Location Change",
            "data": {
                "userid": "user2",
                "amount": 300.00,
                "device_id": "device2"
            }
        },
        {
            "name": "Amount Anomaly",
            "data": {
                "userid": "user3",
                "amount": 4500.00,
                "device_id": "device3"
            }
        },
        {
            "name": "Multiple Transactions",
            "data": [
                {
                    "userid": "user1",
                    "amount": 750.00,
                    "device_id": "device1"
                },
                {
                    "userid": "user1",
                    "amount": 800.00,
                    "device_id": "device1"
                }
            ]
        }
    ]
    
    print("Testing Fraud Detection API\n")
    
    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        
        if isinstance(scenario['data'], list):
            # Handle multiple transactions
            print("Processing multiple transactions...")
            for transaction in scenario['data']:
                print(f"\nTransaction Data: {json.dumps(transaction, indent=2)}")
                process_transaction(base_url, transaction)
                print("-" * 30)
        else:
            # Handle single transaction
            print(f"Request Data: {json.dumps(scenario['data'], indent=2)}")
            process_transaction(base_url, scenario['data'])
        
        print("\n" + "="*50 + "\n")

def process_transaction(base_url, data):
    """Process a single transaction and print results"""
    try:
        response = requests.post(
            f"{base_url}/",  # Root endpoint handles transactions
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        if response.ok:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('fraud_detected'):
                print("\nFraud Detection Details:")
                print("- Status: FRAUDULENT")
                print("- Approval Status:", "Pending Approval" if not result.get('is_approved') else "Approved")
                if result.get('fraud_flags'):
                    print("- Flags:")
                    for flag in result['fraud_flags']:
                        print(f"  * {flag}")
                if result.get('approval_token'):
                    print(f"\nApproval Link: {base_url}/approve/{result['approval_token']}")
            else:
                print("\nTransaction Status: LEGITIMATE")
                print("Automatically Approved: Yes")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_fraud_detection_api() 