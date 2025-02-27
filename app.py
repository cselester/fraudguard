# Main Flask app
from flask import Flask, render_template, request, jsonify
from config import Config
from models import db  # Import db from models/__init__.py
from utils.fraud_detection import detect_fraud
from utils.device_info import get_device_info
import requests

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database after app is created
db.init_app(app)

# Import models after db initialization
from models.transaction import Transaction  

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        userid = request.form["userid"]
        amount = float(request.form["amount"])
        
        # Auto-detect device ID and location
        device_id = get_device_info(request)
        location = requests.get("https://ipinfo.io/json").json().get("city", "Unknown")

        transaction = Transaction(userid=userid, amount=amount, device_id=device_id, location=location)
        db.session.add(transaction)
        db.session.commit()

        # Check for fraud
        is_fraudulent = detect_fraud(amount, location)
        return jsonify({"fraud_detected": is_fraudulent})

    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
