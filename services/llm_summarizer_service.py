"""LLM-based Transaction Summarizer using Google Gemini.

Provides AI-powered insights and summaries using Google's Gemini API.
"""

import os
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMSummarizer:
    """Generate AI-powered summaries using Google Gemini."""

    def __init__(self, api_key: str = None):
        """
        Initialize the LLM summarizer.

        Args:
            api_key: Google API key (if not provided, reads from environment)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Google API key not found. Set GOOGLE_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        print("✅ Gemini LLM initialized successfully")

    def summarize_transactions(self, transactions: List[Dict], 
                               max_transactions: int = 50,
                               focus: str = None) -> str:
        """
        Generate an AI-powered summary of transactions.

        Args:
            transactions: List of transaction dictionaries
            max_transactions: Maximum number of transactions to include
            focus: Optional focus area (e.g., "spending", "savings", "categories")

        Returns:
            AI-generated summary text
        """
        if not transactions:
            return "No transactions found to summarize."
        
        # Limit transactions for API efficiency
        txns_to_summarize = transactions[:max_transactions]
        
        # Create transaction text
        txn_lines = []
        for t in txns_to_summarize:
            line = f"- {t.get('description', 'Unknown')} | "
            line += f"Category: {t.get('category', 'N/A')} | "
            line += f"Amount: ₹{t.get('amount', 0)} | "
            line += f"Type: {t.get('type', 'N/A')} | "
            line += f"Date: {t.get('date', 'N/A')}"
            txn_lines.append(line)
        
        txn_text = "\n".join(txn_lines)
        
        # Create prompt
        focus_instruction = f" Focus particularly on {focus}." if focus else ""
        
        prompt = f"""You are a financial advisor analyzing transaction data. 
Provide a clear, concise summary of the following financial transactions.{focus_instruction}

Include:
1. Overall spending patterns
2. Top spending categories
3. Notable transactions or trends
4. Financial health insights
5. Actionable recommendations

Transactions ({len(txns_to_summarize)} shown):
{txn_text}

Provide a professional, helpful summary in 200-300 words."""

        try:
            # Generate summary
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def get_spending_insights(self, transactions: List[Dict]) -> str:
        """
        Get AI-powered spending insights.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Spending insights text
        """
        return self.summarize_transactions(transactions, focus="spending patterns and budget optimization")

    def get_category_analysis(self, transactions: List[Dict], category: str) -> str:
        """
        Get AI analysis for a specific category.

        Args:
            transactions: List of transaction dictionaries
            category: Category to analyze

        Returns:
            Category analysis text
        """
        # Filter by category
        category_txns = [t for t in transactions if t.get('category') == category]
        
        if not category_txns:
            return f"No transactions found in category: {category}"
        
        return self.summarize_transactions(
            category_txns,
            focus=f"{category} expenses and optimization opportunities"
        )

    def answer_question(self, transactions: List[Dict], question: str) -> str:
        """
        Answer a specific question about transactions using AI.

        Args:
            transactions: List of transaction dictionaries
            question: User's question

        Returns:
            AI-generated answer
        """
        if not transactions:
            return "No transaction data available to answer the question."
        
        # Create transaction summary for context
        txn_summary = []
        for t in transactions[:30]:
            txn_summary.append(
                f"{t.get('description')} - ₹{t.get('amount')} ({t.get('category')}) on {t.get('date')}"
            )
        
        context = "\n".join(txn_summary)
        
        prompt = f"""You are a financial advisor with access to transaction data.

Transaction Data (sample):
{context}

User Question: {question}

Provide a clear, accurate answer based on the transaction data. If the data doesn't contain enough information to answer fully, say so and provide what insights you can."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error answering question: {str(e)}"


if __name__ == "__main__":
    # Example usage
    import json
    
    print("=== LLM Summarizer Example ===\n")
    
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not set in environment")
        print("Set it in your .env file or environment variables")
        exit(1)
    
    # Load transactions
    transactions_file = "./data/transactions.json"
    if os.path.exists(transactions_file):
        with open(transactions_file, 'r') as f:
            transactions = json.load(f)
        
        # Initialize summarizer
        summarizer = LLMSummarizer()
        
        # Generate summary
        print("📊 AI-Generated Summary:\n")
        summary = summarizer.summarize_transactions(transactions[:30])
        print(summary)
        
        print("\n" + "=" * 50)
        print("\n💡 Spending Insights:\n")
        insights = summarizer.get_spending_insights(transactions[:30])
        print(insights)
        
        print("\n" + "=" * 50)
        print("\n❓ Question Answering:\n")
        answer = summarizer.answer_question(
            transactions[:30],
            "What are my biggest expenses this month?"
        )
        print(answer)
    else:
        print(f"❌ Transactions file not found: {transactions_file}")
        print("Run data_generator.py first")
