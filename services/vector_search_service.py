"""Vector Search Service for Financial Transactions.

Provides semantic search capabilities using FAISS and Sentence Transformers.
"""

import os
from typing import List, Dict, Optional
from services.embedding_service import EmbeddingService


class VectorSearchService:
    """High-level service for semantic search on financial transactions."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the vector search service.

        Args:
            model_name: Name of the sentence transformer model
        """
        self.embedding_service = EmbeddingService(model_name)
        self.is_ready = False

    def initialize(self, index_path: str = "./embeddings/vector_store.faiss",
                   transactions_path: str = "./embeddings/transactions.pkl") -> bool:
        """
        Initialize the search service by loading existing index.

        Args:
            index_path: Path to FAISS index
            transactions_path: Path to transactions pickle

        Returns:
            True if successful, False otherwise
        """
        try:
            self.embedding_service.load_index(index_path, transactions_path)
            self.is_ready = True
            return True
        except Exception as e:
            print(f"❌ Failed to initialize search service: {e}")
            self.is_ready = False
            return False

    def search(self, query: str, top_k: int = 10, 
               user_id: Optional[str] = None,
               category: Optional[str] = None,
               min_amount: Optional[float] = None,
               max_amount: Optional[float] = None) -> List[Dict]:
        """
        Search for transactions using natural language query with optional filters.

        Args:
            query: Natural language search query
            top_k: Number of results to return
            user_id: Filter by user ID
            category: Filter by category
            min_amount: Minimum transaction amount
            max_amount: Maximum transaction amount

        Returns:
            List of matching transactions
        """
        if not self.is_ready:
            raise RuntimeError("Search service not initialized. Call initialize() first.")
        
        # Get initial results from vector search
        results = self.embedding_service.search(query, top_k=top_k * 2)  # Get more for filtering
        
        # Apply filters
        filtered_results = []
        for result in results:
            # User filter
            if user_id and result.get('user_id') != user_id:
                continue
            
            # Category filter
            if category and result.get('category') != category:
                continue
            
            # Amount filters
            amount = result.get('amount', 0)
            if min_amount is not None and amount < min_amount:
                continue
            if max_amount is not None and amount > max_amount:
                continue
            
            filtered_results.append(result)
            
            # Stop when we have enough results
            if len(filtered_results) >= top_k:
                break
        
        return filtered_results

    def get_transaction_stats(self) -> Dict:
        """
        Get statistics about indexed transactions.

        Returns:
            Dictionary with transaction statistics
        """
        if not self.is_ready:
            return {"error": "Service not initialized"}
        
        transactions = self.embedding_service.transactions
        
        # Calculate statistics
        total = len(transactions)
        users = set(t['user_id'] for t in transactions)
        categories = {}
        total_amount = 0
        debit_amount = 0
        credit_amount = 0
        
        for t in transactions:
            cat = t.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            amount = t.get('amount', 0)
            total_amount += amount
            
            if t.get('type') == 'debit':
                debit_amount += amount
            elif t.get('type') == 'credit':
                credit_amount += amount
        
        return {
            "total_transactions": total,
            "total_users": len(users),
            "users": sorted(list(users)),
            "categories": categories,
            "total_amount": round(total_amount, 2),
            "total_debit": round(debit_amount, 2),
            "total_credit": round(credit_amount, 2),
            "net_balance": round(credit_amount - debit_amount, 2)
        }

    def get_user_transactions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Get all transactions for a specific user.

        Args:
            user_id: User identifier
            limit: Maximum number of transactions to return

        Returns:
            List of user transactions
        """
        if not self.is_ready:
            raise RuntimeError("Search service not initialized")
        
        user_txns = [t for t in self.embedding_service.transactions 
                     if t.get('user_id') == user_id]
        
        # Sort by date (newest first)
        user_txns.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return user_txns[:limit]

    def get_category_transactions(self, category: str, limit: int = 100) -> List[Dict]:
        """
        Get all transactions for a specific category.

        Args:
            category: Transaction category
            limit: Maximum number of transactions to return

        Returns:
            List of category transactions
        """
        if not self.is_ready:
            raise RuntimeError("Search service not initialized")
        
        cat_txns = [t for t in self.embedding_service.transactions 
                    if t.get('category') == category]
        
        # Sort by date (newest first)
        cat_txns.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return cat_txns[:limit]


if __name__ == "__main__":
    # Example usage
    print("=== Vector Search Service Example ===\n")
    
    # Initialize service
    search_service = VectorSearchService()
    
    if search_service.initialize():
        # Get statistics
        stats = search_service.get_transaction_stats()
        print("📊 Transaction Statistics:")
        print(f"  Total Transactions: {stats['total_transactions']}")
        print(f"  Total Users: {stats['total_users']}")
        print(f"  Total Amount: ₹{stats['total_amount']:,.2f}")
        print(f"  Net Balance: ₹{stats['net_balance']:,.2f}")
        print()
        
        # Test searches
        test_queries = [
            ("restaurant expenses", {}),
            ("flight bookings", {"min_amount": 5000}),
            ("monthly salary", {"category": "Income"}),
        ]
        
        print("=== Test Searches ===\n")
        for query, filters in test_queries:
            print(f"Query: '{query}' with filters: {filters}")
            results = search_service.search(query, top_k=3, **filters)
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['description']}")
                print(f"     Amount: ₹{result['amount']} | Score: {result['similarity_score']:.3f}")
            print()
    else:
        print("❌ Failed to initialize search service")
        print("Make sure to run setup.py first to generate data and build index")
