# ML Model training script
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from ml.random_forest_model import FraudDetectionModel
from flask import Flask
from config import Config
from models import db
from models.transaction import Transaction
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def get_historical_transactions():
    """Get historical transactions from database"""
    transactions = Transaction.query.all()
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

def train_and_save_model():
    """Train and save the Random Forest model"""
    with app.app_context():
        print("Starting model training process...")
        
        # Get historical transaction data
        transaction_data = get_historical_transactions()
        
        if not transaction_data:
            print("No historical transaction data found.")
            return
        
        print(f"Training model with {len(transaction_data)} transactions...")
        print("Sample transaction:", transaction_data[0])
        
        # Initialize and train model
        model = FraudDetectionModel()
        metrics = model.train(transaction_data)
        
        print("Training completed!")
        print(f"Training accuracy: {metrics['train_accuracy']:.2%}")
        print(f"Test accuracy: {metrics['test_accuracy']:.2%}")
        
        # Save the trained model
        model.save_model()
        print("Model saved successfully!")
        
        # Verify the model file exists
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'random_forest_model.pkl')
        if os.path.exists(model_path):
            print(f"Model file verified at: {model_path}")
            print(f"File size: {os.path.getsize(model_path)} bytes")
        else:
            print("Warning: Model file not found after saving!")

if __name__ == "__main__":
    train_and_save_model()
