"""Synthetic Financial Transaction Data Generator.

Generates realistic financial transaction data using Faker library.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
from faker import Faker
import os


class FinancialDataGenerator:
    """Generate synthetic financial transaction data for multiple users."""

    def __init__(self, num_users: int = 3, transactions_per_user_range: tuple = (100, 200)):
        """
        Initialize the data generator.

        Args:
            num_users: Number of users to generate transactions for
            transactions_per_user_range: Tuple of (min, max) transactions per user
        """
        self.fake = Faker()
        self.num_users = num_users
        self.transactions_per_user_range = transactions_per_user_range
        
        # Transaction categories with realistic descriptions
        self.categories = {
            "Food & Dining": [
                "Restaurant", "Cafe", "Fast Food", "Grocery Store", "Food Delivery",
                "Coffee Shop", "Bakery", "Bar", "Fine Dining"
            ],
            "Shopping": [
                "Clothing Store", "Electronics", "Online Shopping", "Department Store",
                "Bookstore", "Pharmacy", "Furniture", "Sporting Goods"
            ],
            "Transportation": [
                "Gas Station", "Uber", "Taxi", "Public Transit", "Parking",
                "Car Maintenance", "Toll", "Car Rental"
            ],
            "Entertainment": [
                "Movie Theater", "Concert", "Streaming Service", "Gaming",
                "Sports Event", "Museum", "Theme Park", "Music Subscription"
            ],
            "Bills & Utilities": [
                "Electricity Bill", "Water Bill", "Internet Bill", "Phone Bill",
                "Gas Bill", "Insurance", "Rent", "Mortgage"
            ],
            "Healthcare": [
                "Doctor Visit", "Pharmacy", "Dental", "Hospital", "Lab Tests",
                "Health Insurance", "Gym Membership", "Wellness"
            ],
            "Travel": [
                "Hotel", "Flight", "Vacation Package", "Travel Insurance",
                "Luggage", "Tourist Attraction", "Resort"
            ],
            "Education": [
                "Tuition", "Books", "Online Course", "Workshop", "Certification",
                "School Supplies", "Training"
            ],
            "Income": [
                "Salary", "Freelance Payment", "Bonus", "Investment Return",
                "Refund", "Gift", "Cashback"
            ]
        }

    def generate_transaction(self, user_id: str, transaction_id: int) -> Dict:
        """
        Generate a single transaction.

        Args:
            user_id: User identifier
            transaction_id: Unique transaction ID

        Returns:
            Dictionary containing transaction details
        """
        category = random.choice(list(self.categories.keys()))
        subcategory = random.choice(self.categories[category])
        
        # Generate realistic amounts based on category
        if category == "Income":
            amount = round(random.uniform(1000, 50000), 2)
            transaction_type = "credit"
        elif category == "Bills & Utilities":
            amount = round(random.uniform(500, 5000), 2)
            transaction_type = "debit"
        elif category == "Travel":
            amount = round(random.uniform(2000, 30000), 2)
            transaction_type = "debit"
        elif category == "Education":
            amount = round(random.uniform(1000, 20000), 2)
            transaction_type = "debit"
        else:
            amount = round(random.uniform(50, 5000), 2)
            transaction_type = "debit"
        
        # Generate date within last 365 days
        days_ago = random.randint(0, 365)
        transaction_date = datetime.now() - timedelta(days=days_ago)
        
        # Generate merchant/payee name
        if category == "Income":
            merchant = self.fake.company()
        else:
            merchant = f"{subcategory} - {self.fake.company()}"
        
        # Create description
        description = f"{subcategory} at {merchant}"
        
        return {
            "transaction_id": f"TXN{transaction_id:06d}",
            "user_id": user_id,
            "date": transaction_date.strftime("%Y-%m-%d"),
            "timestamp": transaction_date.isoformat(),
            "description": description,
            "merchant": merchant,
            "category": category,
            "subcategory": subcategory,
            "amount": amount,
            "currency": "INR",
            "type": transaction_type,
            "payment_method": random.choice(["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash", "Wallet"]),
            "status": random.choice(["completed", "completed", "completed", "pending"]),
            "location": self.fake.city(),
            "notes": self.fake.sentence() if random.random() > 0.7 else ""
        }

    def generate_user_transactions(self, user_id: str, num_transactions: int, start_id: int) -> List[Dict]:
        """
        Generate transactions for a single user.

        Args:
            user_id: User identifier
            num_transactions: Number of transactions to generate
            start_id: Starting transaction ID

        Returns:
            List of transaction dictionaries
        """
        transactions = []
        for i in range(num_transactions):
            transaction = self.generate_transaction(user_id, start_id + i)
            transactions.append(transaction)
        
        # Sort by date (newest first)
        transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        return transactions

    def generate_all_transactions(self) -> List[Dict]:
        """
        Generate transactions for all users.

        Returns:
            List of all transactions
        """
        all_transactions = []
        transaction_id_counter = 1
        
        for user_num in range(1, self.num_users + 1):
            user_id = f"USER{user_num:03d}"
            num_transactions = random.randint(*self.transactions_per_user_range)
            
            user_transactions = self.generate_user_transactions(
                user_id, num_transactions, transaction_id_counter
            )
            all_transactions.extend(user_transactions)
            transaction_id_counter += num_transactions
        
        return all_transactions

    def save_to_file(self, transactions: List[Dict], filepath: str) -> None:
        """
        Save transactions to a JSON file.

        Args:
            transactions: List of transaction dictionaries
            filepath: Path to save the JSON file
        """
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(transactions, f, indent=2, ensure_ascii=False)
            print(f"✅ Successfully saved {len(transactions)} transactions to {filepath}")
        except Exception as e:
            print(f"❌ Error saving transactions: {e}")
            raise

    def generate_and_save(self, filepath: str = "./data/transactions.json") -> List[Dict]:
        """
        Generate transactions and save to file.

        Args:
            filepath: Path to save the JSON file

        Returns:
            List of generated transactions
        """
        print(f"🔄 Generating transactions for {self.num_users} users...")
        transactions = self.generate_all_transactions()
        print(f"✅ Generated {len(transactions)} transactions")
        
        self.save_to_file(transactions, filepath)
        return transactions


if __name__ == "__main__":
    # Example usage
    generator = FinancialDataGenerator(num_users=3, transactions_per_user_range=(100, 200))
    transactions = generator.generate_and_save()
    
    # Print summary
    print("\n📊 Transaction Summary:")
    print(f"Total Transactions: {len(transactions)}")
    
    users = set(t['user_id'] for t in transactions)
    for user in sorted(users):
        user_txns = [t for t in transactions if t['user_id'] == user]
        print(f"  {user}: {len(user_txns)} transactions")
    
    categories = {}
    for t in transactions:
        categories[t['category']] = categories.get(t['category'], 0) + 1
    
    print("\n📈 Category Distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
