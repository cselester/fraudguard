# Main Flask app
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from models import db  # Import db from models/__init__.py
from models.transaction import Transaction
from utils.fraud_detection import detect_fraud
from utils.device_info import get_device_info
import requests
from werkzeug.exceptions import BadRequest
import traceback
from datetime import datetime, timezone
import json

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database after app is created
db.init_app(app)

# Import models after db initialization
from models.transaction import Transaction  

# Add JSON filter for Jinja2
@app.template_filter('fromjson')
def fromjson_filter(value):
    if not value:
        return []
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return []

# Create tables
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Get JSON data from request
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data received")

            userid = data.get("userid")
            amount = data.get("amount")

            # Validate required fields
            if not userid or amount is None:
                raise BadRequest("Missing required fields: userid and amount")

            try:
                amount = float(amount)
                if amount <= 0:
                    raise BadRequest("Amount must be greater than 0")
            except (TypeError, ValueError):
                raise BadRequest("Invalid amount format - must be a valid number")

            # Auto-detect device ID and location
            device_id = get_device_info(request)
            try:
                location_response = requests.get("https://ipinfo.io/json", timeout=5)
                location = location_response.json().get("city", "Unknown")
            except requests.exceptions.RequestException:
                location = "Unknown"

            # Check for fraud before saving transaction
            is_fraudulent, fraud_flags = detect_fraud(amount, location, userid)

            # Create transaction
            transaction = Transaction(
                userid=userid,
                amount=amount,
                device_id=device_id,
                location=location,
                is_fraudulent=is_fraudulent,
                fraud_flags=fraud_flags
            )

            # Automatically approve if not fraudulent
            if not is_fraudulent:
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

            return jsonify({
                "success": True,
                "fraud_detected": is_fraudulent,
                "is_approved": transaction.is_approved,
                "fraud_flags": json.loads(fraud_flags) if fraud_flags else None,
                "transaction_id": transaction.id
            })

        except BadRequest as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print(traceback.format_exc())
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": "An unexpected error occurred while processing your transaction"
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
