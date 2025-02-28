import requests
import json

def register_test_users():
    """Register test users for fraud detection testing"""
    base_url = "http://127.0.0.1:5000"
    
    # Test users
    users = [
        {
            "username": "user1",
            "userid": "user1",
            "email": "user1@example.com",
            "phone": "+15550001"
        },
        {
            "username": "user2",
            "userid": "user2",
            "email": "user2@example.com",
            "phone": "+15550002"
        },
        {
            "username": "user3",
            "userid": "user3",
            "email": "user3@example.com",
            "phone": "+15550003"
        }
    ]
    
    print("Registering test users...\n")
    
    for user in users:
        print(f"Registering user: {user['username']}")
        try:
            response = requests.post(
                f"{base_url}/register",
                json=user,
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            if response.ok:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {str(e)}")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    register_test_users() 