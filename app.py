# Main Flask app
from flask import Flask, render_template, request, jsonify, redirect, url_for
from config import Config
from models import db  # Import db from models/__init__.py
from utils.fraud_detection import detect_fraud
from utils.device_info import get_device_info
import requests
from werkzeug.exceptions import BadRequest
import traceback
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database after app is created
db.init_app(app)

# Import models after db initialization
from models.transaction import Transaction  

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
            if not userid or not amount:
                raise BadRequest("Missing required fields: userid and amount")

            try:
                amount = float(amount)
            except (TypeError, ValueError):
                raise BadRequest("Invalid amount format")

            # Auto-detect device ID and location
            device_id = get_device_info(request)
            try:
                location_response = requests.get("https://ipinfo.io/json", timeout=5)
                location = location_response.json().get("city", "Unknown")
            except requests.exceptions.RequestException:
                location = "Unknown"

            # Create and save transaction
            transaction = Transaction(userid=userid, amount=amount, device_id=device_id, location=location)
            db.session.add(transaction)
            db.session.commit()

            # Check for fraud
            is_fraudulent = detect_fraud(amount, location)
            return jsonify({
                "success": True,
                "fraud_detected": is_fraudulent
            })

        except BadRequest as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": "An unexpected error occurred"
            }), 500

    return render_template("index.html")

@app.route("/admin")
def admin():
    """Admin dashboard showing all transactions and statistics"""
    transactions = Transaction.query.order_by(Transaction.timestamp.desc()).all()
    
    # Calculate statistics
    stats = {
        "total": len(transactions),
        "pending": sum(1 for t in transactions if not t.is_approved and not t.is_fraudulent),
        "approved": sum(1 for t in transactions if t.is_approved),
        "fraudulent": sum(1 for t in transactions if t.is_fraudulent)
    }
    
    return render_template("admin.html", transactions=transactions, stats=stats)

@app.route("/admin/approve/<int:transaction_id>", methods=["POST"])
def admin_approve_transaction(transaction_id):
    """Approve a transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    transaction.is_approved = True
    transaction.approval_timestamp = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("admin"))

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
