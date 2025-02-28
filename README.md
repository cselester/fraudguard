# FraudGuard: Real-time Transaction Fraud Detection System

FraudGuard is a sophisticated fraud detection system that combines machine learning and rule-based approaches to identify and prevent fraudulent transactions in real-time. The system uses a Random Forest classifier along with traditional rule-based checks to provide comprehensive fraud detection capabilities.

## Features

- **Hybrid Detection System**
  - Machine Learning (Random Forest) based detection
  - Rule-based detection as fallback
  - Combined approach for maximum accuracy

- **Real-time Transaction Monitoring**
  - Instant transaction analysis
  - Multiple fraud detection rules
  - Transaction pattern analysis
  - Location-based monitoring
  - Amount anomaly detection

- **User Management**
  - User registration and authentication
  - Transaction history tracking
  - User-specific fraud patterns

- **Alert System**
  - SMS notifications for suspicious transactions
  - Email alerts with transaction details
  - Approval links for transaction verification

- **Admin Dashboard**
  - Transaction monitoring
  - Fraud statistics
  - Manual transaction approval/decline
  - User management

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLAlchemy (SQL Database)
- **Machine Learning**: scikit-learn, numpy, pandas
- **Authentication**: Token-based authentication
- **Notifications**: Email and SMS integration

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fraudguard.git
cd fraudguard
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python app.py
```

## Configuration

The system can be configured through the `config.py` file and environment variables:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Application secret key
- `SMS_API_KEY`: SMS service API key
- `EMAIL_SERVER`: SMTP server settings
- `ML_MODEL_PATH`: Path to save/load ML model

## Usage

1. **Start the Application**:
```bash
python app.py
```

2. **Register Test Users**:
```bash
python register_test_users.py
```

3. **Train the ML Model**:
```bash
python ml/train_model.py
```

4. **Test the System**:
```bash
python test_fraud_detection.py
```

## Fraud Detection Rules

1. **Amount-based Rules**
   - High amount transactions (> $10,000)
   - Amount anomaly (5x user average)
   - Rapid small transactions

2. **Location-based Rules**
   - Rapid location changes
   - Transactions from suspicious locations
   - Multiple locations in short time

3. **Pattern-based Rules**
   - Multiple declined transactions
   - High frequency transactions
   - Unusual time patterns

4. **ML-based Detection**
   - Transaction amount patterns
   - User behavior analysis
   - Historical pattern matching
   - Location frequency analysis

## API Endpoints

### User Management
- `POST /register`: Register new user
- `GET /register`: Registration form

### Transaction Processing
- `POST /`: Process new transaction
- `GET /`: Transaction form

### Transaction Approval
- `GET /approve/<token>`: Approve transaction via token
- `POST /admin/approve/<id>`: Admin approval
- `POST /admin/decline/<id>`: Admin decline

### Admin Interface
- `GET /admin`: Admin dashboard

## Response Format

### Success Response
```json
{
    "success": true,
    "fraud_detected": false,
    "is_approved": true,
    "fraud_flags": null,
    "transaction_id": 123
}
```

### Fraud Detection Response
```json
{
    "success": true,
    "fraud_detected": true,
    "is_approved": false,
    "fraud_flags": [
        "Amount exceeds threshold",
        "Unusual location pattern"
    ],
    "approval_token": "xyz123..."
}
```

## Testing

The system includes comprehensive test scripts:
- `test_fraud_detection.py`: Test fraud detection scenarios
- `register_test_users.py`: Create test users
- `test_api.py`: Test API endpoints

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- scikit-learn for machine learning capabilities
- Flask for the web framework
- SQLAlchemy for database operations 