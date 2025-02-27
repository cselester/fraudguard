import os
from flask import url_for
import logging
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "tushartripathi2002@gmail.com"  # Replace with your email
SMTP_PASSWORD = "pera mhae iwwx cmis"      # Replace with your app password

def send_transaction_email(user, transaction):
    """Send transaction details via email"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = user.email
        msg['Subject'] = "🚨 FraudGuard: Suspicious Transaction Alert"

        # Get current time if timestamp is None
        transaction_time = transaction.timestamp or datetime.now(timezone.utc)

        # Email body
        body = f"""
        Dear {user.username},

        We detected a suspicious transaction on your account.

        Transaction Details:
        -------------------
        • Amount: ${transaction.amount:,.2f}
        • Location: {transaction.location}
        • Time: {transaction_time.strftime('%Y-%m-%d %H:%M:%S')}
        • Device ID: {transaction.device_id}

        This transaction has been flagged for your security.
        Please check your phone for an SMS containing the approval link.

        If you did not initiate this transaction, please contact our support team immediately.

        Best regards,
        FraudGuard Security Team
        """

        msg.attach(MIMEText(body, 'plain'))

        # Connect to SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Transaction alert email sent to {user.email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def send_fraud_alert(user, transaction):
    """Send fraud alerts via SMS and email"""
    
    # Generate approval token if not exists
    if not transaction.approval_token:
        transaction.generate_approval_token()
    
    # Create approval URL for SMS only
    approval_url = url_for(
        'approve_transaction_token',
        token=transaction.approval_token,
        _external=True
    )
    
    # Compose SMS message with approval link
    sms_message = (
        f"🚨 FraudGuard Alert!\n"
        f"Amount: ${transaction.amount:,.2f}\n"
        f"Location: {transaction.location}\n"
        f"Approve: {approval_url}"
    )
    
    # Log SMS alert (simulated)
    logger.info(f"\n[SMS Alert to {user.phone}]\n{sms_message}")
    
    # Send email with transaction details (no approval link)
    send_transaction_email(user, transaction)
    
    return True 