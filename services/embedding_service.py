"""Embedding Service for Financial Transactions.

Creates embeddings using Sentence Transformers and manages FAISS vector database.
"""

import json
import os
import pickle
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


class EmbeddingService:
    """Service for creating and managing transaction embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.

        Args:
            model_name: Name of the sentence transformer model to use
        """
        print(f"🔄 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.transactions = []
        print(f"✅ Model loaded. Embedding dimension: {self.dimension}")

    def create_transaction_text(self, transaction: Dict) -> str:
        """
        Create a searchable text representation of a transaction.

        Args:
            transaction: Transaction dictionary

        Returns:
            Formatted text string for embedding
        """
        parts = [
            transaction.get('description', ''),
            transaction.get('category', ''),
            transaction.get('subcategory', ''),
            transaction.get('merchant', ''),
            f"Amount: {transaction.get('amount', 0)} {transaction.get('currency', 'INR')}",
            f"Type: {transaction.get('type', '')}",
            f"Payment: {transaction.get('payment_method', '')}",
            transaction.get('notes', '')
        ]
        return " | ".join([p for p in parts if p])

    def create_embeddings(self, transactions: List[Dict]) -> np.ndarray:
        """
        Create embeddings for a list of transactions.

        Args:
            transactions: List of transaction dictionaries

        Returns:
            Numpy array of embeddings
        """
        print(f"🔄 Creating embeddings for {len(transactions)} transactions...")
        texts = [self.create_transaction_text(t) for t in transactions]
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        print(f"✅ Created embeddings with shape: {embeddings.shape}")
        return embeddings

    def build_index(self, transactions: List[Dict]) -> None:
        """
        Build FAISS index from transactions.

        Args:
            transactions: List of transaction dictionaries
        """
        self.transactions = transactions
        embeddings = self.create_embeddings(transactions)
        
        # Create FAISS index
        print("🔄 Building FAISS index...")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        print(f"✅ FAISS index built with {self.index.ntotal} vectors")

    def save_index(self, index_path: str = "./embeddings/vector_store.faiss", 
                   transactions_path: str = "./embeddings/transactions.pkl") -> None:
        """
        Save FAISS index and transactions to disk.

        Args:
            index_path: Path to save FAISS index
            transactions_path: Path to save transactions pickle
        """
        try:
            os.makedirs(os.path.dirname(index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save transactions
            with open(transactions_path, 'wb') as f:
                pickle.dump(self.transactions, f)
            
            print(f"✅ Saved FAISS index to {index_path}")
            print(f"✅ Saved transactions to {transactions_path}")
        except Exception as e:
            print(f"❌ Error saving index: {e}")
            raise

    def load_index(self, index_path: str = "./embeddings/vector_store.faiss",
                   transactions_path: str = "./embeddings/transactions.pkl") -> None:
        """
        Load FAISS index and transactions from disk.

        Args:
            index_path: Path to FAISS index
            transactions_path: Path to transactions pickle
        """
        try:
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"Index not found at {index_path}")
            
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load transactions
            with open(transactions_path, 'rb') as f:
                self.transactions = pickle.load(f)
            
            print(f"✅ Loaded FAISS index with {self.index.ntotal} vectors")
            print(f"✅ Loaded {len(self.transactions)} transactions")
        except Exception as e:
            print(f"❌ Error loading index: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar transactions using natural language query.

        Args:
            query: Natural language search query
            top_k: Number of results to return

        Returns:
            List of matching transactions with similarity scores
        """
        if self.index is None:
            raise ValueError("Index not built. Call build_index() or load_index() first.")
        
        # Create query embedding
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # Prepare results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.transactions):
                result = self.transactions[idx].copy()
                result['similarity_score'] = float(1 / (1 + distance))  # Convert distance to similarity
                result['distance'] = float(distance)
                results.append(result)
        
        return results


if __name__ == "__main__":
    # Example usage
    print("=== Embedding Service Example ===\n")
    
    # Load transactions
    transactions_file = "./data/transactions.json"
    if os.path.exists(transactions_file):
        with open(transactions_file, 'r') as f:
            transactions = json.load(f)
        
        # Create service
        service = EmbeddingService()
        
        # Build index
        service.build_index(transactions)
        
        # Save index
        service.save_index()
        
        # Test search
        test_queries = [
            "food expenses",
            "travel bookings",
            "salary income",
            "healthcare costs"
        ]
        
        print("\n=== Test Searches ===\n")
        for query in test_queries:
            print(f"Query: '{query}'")
            results = service.search(query, top_k=3)
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['description']} - ₹{result['amount']} (Score: {result['similarity_score']:.3f})")
            print()
    else:
        print(f"❌ Transactions file not found: {transactions_file}")
        print("Run data_generator.py first to generate transactions.")
