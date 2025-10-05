"""Rule-based Transaction Summarizer.

Provides statistical summaries and insights from financial transactions.
"""

from typing import List, Dict
from collections import defaultdict
from datetime import datetime


class TransactionSummarizer:
    """Generate rule-based summaries from transaction data."""

    @staticmethod
    def summarize_transactions(transactions: List[Dict]) -> Dict:
        """
        Create a comprehensive summary of transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Dictionary containing summary statistics and insights
        """
        if not transactions:
            return {"message": "No transactions to summarize"}
        
        # Initialize counters
        total_count = len(transactions)
        category_stats = defaultdict(lambda: {"count": 0, "total": 0, "transactions": []})
        user_stats = defaultdict(lambda: {"count": 0, "debit": 0, "credit": 0})
        payment_method_stats = defaultdict(int)
        monthly_stats = defaultdict(lambda: {"debit": 0, "credit": 0, "count": 0})
        
        total_debit = 0
        total_credit = 0
        
        # Process transactions
        for txn in transactions:
            amount = txn.get('amount', 0)
            category = txn.get('category', 'Unknown')
            user_id = txn.get('user_id', 'Unknown')
            txn_type = txn.get('type', 'debit')
            payment_method = txn.get('payment_method', 'Unknown')
            
            # Category stats
            category_stats[category]["count"] += 1
            category_stats[category]["total"] += amount
            category_stats[category]["transactions"].append(txn)
            
            # User stats
            user_stats[user_id]["count"] += 1
            if txn_type == 'debit':
                user_stats[user_id]["debit"] += amount
                total_debit += amount
            else:
                user_stats[user_id]["credit"] += amount
                total_credit += amount
            
            # Payment method stats
            payment_method_stats[payment_method] += 1
            
            # Monthly stats
            try:
                date_obj = datetime.fromisoformat(txn.get('timestamp', ''))
                month_key = date_obj.strftime('%Y-%m')
                monthly_stats[month_key]["count"] += 1
                if txn_type == 'debit':
                    monthly_stats[month_key]["debit"] += amount
                else:
                    monthly_stats[month_key]["credit"] += amount
            except:
                pass
        
        # Find top categories
        top_categories = sorted(
            category_stats.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:5]
        
        # Find top spending category
        top_spending_category = max(
            [(cat, stats['total']) for cat, stats in category_stats.items() 
             if cat != 'Income'],
            key=lambda x: x[1],
            default=('None', 0)
        )
        
        # Build summary
        summary = {
            "overview": {
                "total_transactions": total_count,
                "total_debit": round(total_debit, 2),
                "total_credit": round(total_credit, 2),
                "net_balance": round(total_credit - total_debit, 2),
                "average_transaction": round((total_debit + total_credit) / total_count, 2)
            },
            "by_category": {
                cat: {
                    "count": stats["count"],
                    "total_amount": round(stats["total"], 2),
                    "average_amount": round(stats["total"] / stats["count"], 2)
                }
                for cat, stats in category_stats.items()
            },
            "top_categories": [
                {
                    "category": cat,
                    "total_amount": round(stats["total"], 2),
                    "transaction_count": stats["count"]
                }
                for cat, stats in top_categories
            ],
            "by_user": {
                user: {
                    "transaction_count": stats["count"],
                    "total_debit": round(stats["debit"], 2),
                    "total_credit": round(stats["credit"], 2),
                    "net_balance": round(stats["credit"] - stats["debit"], 2)
                }
                for user, stats in user_stats.items()
            },
            "by_payment_method": dict(payment_method_stats),
            "insights": {
                "top_spending_category": top_spending_category[0],
                "top_spending_amount": round(top_spending_category[1], 2),
                "savings_rate": round((total_credit - total_debit) / total_credit * 100, 2) if total_credit > 0 else 0
            }
        }
        
        return summary

    @staticmethod
    def generate_text_summary(transactions: List[Dict]) -> str:
        """
        Generate a human-readable text summary.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Formatted text summary
        """
        summary = TransactionSummarizer.summarize_transactions(transactions)
        
        if "message" in summary:
            return summary["message"]
        
        overview = summary["overview"]
        insights = summary["insights"]
        
        text = f"""
📊 Financial Summary
{'=' * 50}

Overview:
  • Total Transactions: {overview['total_transactions']}
  • Total Spent: ₹{overview['total_debit']:,.2f}
  • Total Earned: ₹{overview['total_credit']:,.2f}
  • Net Balance: ₹{overview['net_balance']:,.2f}
  • Average Transaction: ₹{overview['average_transaction']:,.2f}

Top Spending Categories:
"""
        
        for i, cat in enumerate(summary['top_categories'][:3], 1):
            text += f"  {i}. {cat['category']}: ₹{cat['total_amount']:,.2f} ({cat['transaction_count']} transactions)\n"
        
        text += f"""
Key Insights:
  • Highest spending category: {insights['top_spending_category']} (₹{insights['top_spending_amount']:,.2f})
  • Savings rate: {insights['savings_rate']}%

"""
        
        return text.strip()


if __name__ == "__main__":
    # Example usage
    import json
    import os
    
    transactions_file = "./data/transactions.json"
    if os.path.exists(transactions_file):
        with open(transactions_file, 'r') as f:
            transactions = json.load(f)
        
        # Generate summary
        summarizer = TransactionSummarizer()
        
        # Text summary
        print(summarizer.generate_text_summary(transactions[:50]))
        
        # Detailed summary
        print("\n" + "=" * 50)
        print("Detailed Summary (JSON):")
        print("=" * 50)
        summary = summarizer.summarize_transactions(transactions[:50])
        print(json.dumps(summary, indent=2))
    else:
        print(f"❌ Transactions file not found: {transactions_file}")
