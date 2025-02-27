from flask import Flask
from models import db
from models.transaction import Transaction
from config import Config
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def view_all_transactions():
    """Display all transactions in the database"""
    with app.app_context():
        transactions = Transaction.query.all()
        if not transactions:
            print("No transactions found in database.")
            return
        
        print("\n=== All Transactions ===")
        print(f"{'ID':<5} {'User ID':<10} {'Amount':<10} {'Location':<15} {'Device ID':<30} {'Timestamp':<20}")
        print("-" * 90)
        
        for t in transactions:
            print(f"{t.id:<5} {t.userid:<10} ${t.amount:<9.2f} {t.location:<15} {t.device_id[:30]:<30} {t.timestamp}")

def search_by_userid(userid):
    """Search transactions by user ID"""
    with app.app_context():
        transactions = Transaction.query.filter_by(userid=userid).all()
        if not transactions:
            print(f"No transactions found for user ID: {userid}")
            return
        
        print(f"\n=== Transactions for User {userid} ===")
        print(f"{'ID':<5} {'Amount':<10} {'Location':<15} {'Timestamp':<20}")
        print("-" * 50)
        
        for t in transactions:
            print(f"{t.id:<5} ${t.amount:<9.2f} {t.location:<15} {t.timestamp}")

def show_statistics():
    """Show basic statistics about transactions"""
    with app.app_context():
        total_transactions = Transaction.query.count()
        if total_transactions == 0:
            print("No transactions in database.")
            return

        total_amount = db.session.query(db.func.sum(Transaction.amount)).scalar()
        avg_amount = db.session.query(db.func.avg(Transaction.amount)).scalar()
        unique_users = db.session.query(Transaction.userid).distinct().count()
        unique_locations = db.session.query(Transaction.location).distinct().count()

        print("\n=== Transaction Statistics ===")
        print(f"Total Transactions: {total_transactions}")
        print(f"Total Amount: ${total_amount:,.2f}")
        print(f"Average Amount: ${avg_amount:,.2f}")
        print(f"Unique Users: {unique_users}")
        print(f"Unique Locations: {unique_locations}")

def main():
    while True:
        print("\n=== Database Viewer ===")
        print("1. View all transactions")
        print("2. Search by User ID")
        print("3. Show statistics")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            view_all_transactions()
        elif choice == "2":
            userid = input("Enter User ID to search: ")
            search_by_userid(userid)
        elif choice == "3":
            show_statistics()
        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()