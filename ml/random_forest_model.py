import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import json
import os

class FraudDetectionModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def prepare_features(self, transaction_data):
        """
        Prepare features from transaction data
        """
        features = []
        for transaction in transaction_data:
            # Extract time-based features
            transaction_time = datetime.strptime(transaction['timestamp'], '%Y-%m-%d %H:%M:%S')
            hour = transaction_time.hour
            day_of_week = transaction_time.weekday()
            
            # Calculate transaction frequency features
            user_transactions = [t for t in transaction_data if t['userid'] == transaction['userid']]
            recent_transactions = [t for t in user_transactions 
                                if (transaction_time - datetime.strptime(t['timestamp'], '%Y-%m-%d %H:%M:%S')).days <= 7]
            
            avg_amount = np.mean([t['amount'] for t in user_transactions]) if user_transactions else 0
            transaction_frequency = len(recent_transactions)
            
            # Location-based features
            location_frequency = len([t for t in user_transactions if t['location'] == transaction['location']])
            
            # Combine features
            feature_vector = [
                transaction['amount'],
                avg_amount,
                transaction['amount'] / (avg_amount if avg_amount > 0 else 1),
                transaction_frequency,
                location_frequency,
                hour,
                day_of_week
            ]
            features.append(feature_vector)
            
        return np.array(features)
    
    def train(self, transaction_data):
        """
        Train the Random Forest model
        """
        # Prepare features and labels
        X = self.prepare_features(transaction_data)
        y = np.array([t['is_fraudulent'] for t in transaction_data])
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Calculate accuracy
        train_accuracy = self.model.score(X_train_scaled, y_train)
        test_accuracy = self.model.score(X_test_scaled, y_test)
        
        return {
            'train_accuracy': train_accuracy,
            'test_accuracy': test_accuracy
        }
    
    def predict(self, transaction):
        """
        Predict if a transaction is fraudulent
        """
        # Prepare single transaction features
        features = self.prepare_features([transaction])
        features_scaled = self.scaler.transform(features)
        
        # Get prediction and probability
        prediction = self.model.predict(features_scaled)[0]
        probability = self.model.predict_proba(features_scaled)[0]
        
        # Get feature importance for explanation
        feature_importance = dict(zip(
            ['amount', 'avg_amount', 'amount_ratio', 'transaction_freq', 
             'location_freq', 'hour', 'day_of_week'],
            self.model.feature_importances_
        ))
        
        return {
            'is_fraudulent': bool(prediction),
            'confidence': float(probability[1]),  # Probability of fraud
            'feature_importance': feature_importance
        }
    
    def save_model(self, filepath=None):
        """Save the trained model"""
        if filepath is None:
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, 'random_forest_model.pkl')
        
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath=None):
        """Load a trained model"""
        if filepath is None:
            # Get the directory of the current file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(current_dir, 'random_forest_model.pkl')
        
        try:
            saved_model = joblib.load(filepath)
            self.model = saved_model['model']
            self.scaler = saved_model['scaler']
            print(f"Model loaded from {filepath}")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise 