# Transaction submission & fraud detection
from flask import Blueprint, request, jsonify
from models.transaction import Transaction
from app import db
from utils.fraud_detection import detect_fraud

transaction_bp = Blueprint("transactions", __name__)

@transaction_bp.route("/submit", methods=["POST"])
def submit_transaction():
    data = request.json
    userid = data.get("userid")
    amount = data.get("amount")

    transaction = Transaction(userid=userid, amount=amount)
    db.session.add(transaction)
    db.session.commit()

    is_fraudulent = detect_fraud(amount)
    return jsonify({"fraud_detected": is_fraudulent})
