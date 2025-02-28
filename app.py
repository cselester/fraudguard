# Main Flask app
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from models import db  # Import db from models/__init__.py
from models.transaction import Transaction
from models.user import User
from utils.fraud_detection import detect_fraud
from utils.device_info import get_device_info
from utils.notifications import send_fraud_alert
import requests
from werkzeug.exceptions import BadRequest
import traceback
from datetime import datetime, timezone
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    # Drop all tables and recreate them
    db.drop_all()
    db.create_all()
    print("Database tables created successfully!")

@app.template_filter('fromjson')
def fromjson_filter(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data received")

            # Validate required fields
            required_fields = ['username', 'userid', 'email', 'phone']
            for field in required_fields:
                if not data.get(field):
                    raise BadRequest(f"Missing required field: {field}")

            # Create new user
            user = User(
                username=data['username'],
                userid=data['userid'],
                email=data['email'],
                phone=data['phone']
            )

            try:
                db.session.add(user)
                db.session.commit()
                return jsonify({
                    "success": True,
                    "message": "User registered successfully"
                })
            except Exception as e:
                db.session.rollback()
                print(f"Database error during registration: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": "User registration failed. Email or phone might already be registered."
                }), 400

        except BadRequest as e:
            print(f"Bad request during registration: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            print(f"Unexpected error during registration: {str(e)}")
            return jsonify({"success": False, "error": "Registration failed"}), 500

    return render_template("register.html")

@app.route("/approve/<token>")
def approve_transaction_token(token):
    """Approve transaction using token from SMS link"""
    transaction = Transaction.query.filter_by(
        approval_token=token,
        is_approved=False,
        is_declined=False
    ).first_or_404()

    # Check if token is expired
    current_time = datetime.now(timezone.utc)
    if not transaction.token_expiry:
        return render_template("approve.html", error="Invalid approval token")
        
    if transaction.token_expiry.replace(tzinfo=timezone.utc) < current_time:
        return render_template("approve.html", error="Approval link has expired")

    # Approve transaction
    transaction.is_approved = True
    transaction.approval_timestamp = current_time
    transaction.approval_token = None  # Invalidate token
    db.session.commit()

    return render_template("approve.html", success=True, transaction=transaction)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data received")

            userid = data.get("userid")
            amount = data.get("amount")

            # Validate required fields
            if not userid or amount is None:
                raise BadRequest("Missing required fields: userid and amount")

            # Verify user exists
            user = User.query.filter_by(userid=userid).first()
            if not user:
                raise BadRequest("Invalid user ID")

            try:
                amount = float(amount)
                if amount <= 0:
                    raise BadRequest("Amount must be greater than 0")
            except (TypeError, ValueError):
                raise BadRequest("Invalid amount format")

            device_id = get_device_info(request)
            try:
                location_response = requests.get("https://ipinfo.io/json", timeout=5)
                location = location_response.json().get("city", "Unknown")
            except:
                location = "Unknown"

            is_fraudulent, fraud_flags = detect_fraud(amount, location, userid)

            transaction = Transaction(
                userid=userid,
                amount=amount,
                device_id=device_id,
                location=location,
                is_fraudulent=is_fraudulent,
                fraud_flags=fraud_flags,
                timestamp=datetime.now(timezone.utc)  # Explicitly set timestamp
            )

            if is_fraudulent:
                # Generate approval token and send alerts
                transaction.generate_approval_token()
                send_fraud_alert(user, transaction)
            else:
                # Auto-approve safe transactions
                transaction.is_approved = True
                transaction.approval_timestamp = datetime.now(timezone.utc)

            try:
                db.session.add(transaction)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Database error: {str(e)}")
                return jsonify({
                    "success": False,
                    "error": "Failed to save transaction"
                }), 500

            response_data = {
                "success": True,
                "fraud_detected": is_fraudulent,
                "is_approved": transaction.is_approved,
                "fraud_flags": json.loads(fraud_flags) if fraud_flags else None,
                "transaction_id": transaction.id
            }
            
            # Include approval token for suspicious transactions
            if is_fraudulent:
                response_data["approval_token"] = transaction.approval_token

            return jsonify(response_data)

        except BadRequest as e:
            return jsonify({"success": False, "error": str(e)}), 400
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                "success": False,
                "error": "An unexpected error occurred"
            }), 500

    return render_template("index.html")

@app.route("/admin")
def admin():
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    stats = {
        "total": Transaction.query.count(),
        "fraudulent": Transaction.query.filter_by(is_fraudulent=True).count(),
        "approved": Transaction.query.filter_by(is_approved=True).count(),
        "declined": Transaction.query.filter_by(is_declined=True).count(),
        "pending": Transaction.query.filter_by(is_approved=False, is_declined=False).count()
    }
    return render_template("admin.html", transactions=transactions, stats=stats)

@app.route("/admin/approve/<int:transaction_id>", methods=["POST"])
def admin_approve_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if not transaction.is_approved and not transaction.is_declined:
        transaction.is_approved = True
        transaction.approval_timestamp = datetime.now(timezone.utc)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route("/admin/decline/<int:transaction_id>", methods=["POST"])
def admin_decline_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if not transaction.is_approved and not transaction.is_declined:
        transaction.is_declined = True
        db.session.commit()
    return redirect(url_for('admin'))

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"success": False, "error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"success": False, "error": "Internal server error"}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
