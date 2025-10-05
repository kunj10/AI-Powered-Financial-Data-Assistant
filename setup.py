"""Setup Script for AI Financial Data Assistant.

Initializes the system by:
1. Generating synthetic transaction data
2. Creating embeddings
3. Building FAISS vector index
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from services.data_generator import FinancialDataGenerator
from services.embedding_service import EmbeddingService

# Load environment variables
load_dotenv()


def main():
    """Run the complete setup process."""
    print("=" * 60)
    print("  AI FINANCIAL DATA ASSISTANT - SETUP")
    print("=" * 60)
    print()
    
    # Configuration from environment
    num_users = int(os.getenv("NUM_USERS", 3))
    min_txns = int(os.getenv("TRANSACTIONS_PER_USER_MIN", 100))
    max_txns = int(os.getenv("TRANSACTIONS_PER_USER_MAX", 200))
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    transactions_path = os.getenv("TRANSACTIONS_DATA_PATH", "./data/transactions.json")
    index_path = os.getenv("VECTOR_DB_PATH", "./embeddings/vector_store.faiss")
    
    print(f"Configuration:")
    print(f"  • Users: {num_users}")
    print(f"  • Transactions per user: {min_txns}-{max_txns}")
    print(f"  • Embedding model: {embedding_model}")
    print()
    
    # Step 1: Generate synthetic data
    print("STEP 1: Generating Synthetic Transaction Data")
    print("-" * 60)
    
    generator = FinancialDataGenerator(
        num_users=num_users,
        transactions_per_user_range=(min_txns, max_txns)
    )
    transactions = generator.generate_and_save(transactions_path)
    
    print(f"\n✅ Generated {len(transactions)} transactions")
    print()
    
    # Step 2: Create embeddings and build index
    print("STEP 2: Creating Embeddings and Building FAISS Index")
    print("-" * 60)
    
    embedding_service = EmbeddingService(model_name=embedding_model)
    embedding_service.build_index(transactions)
    
    # Save index
    transactions_pkl_path = index_path.replace("vector_store.faiss", "transactions.pkl")
    embedding_service.save_index(index_path, transactions_pkl_path)
    
    print("=" * 60)
    print("  ✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Set your GOOGLE_API_KEY in .env file (for LLM features)")
    print("  2. Start the API server:")
    print("     python api/app.py")
    print("     or")
    print("     uvicorn api.app:app --reload")
    print()
    print("  3. Access API documentation:")
    print("     http://localhost:8000/docs")
    print()
    print("  4. Test the endpoints using Postman collection:")
    print("     examples/FinancialDataAssistant.postman_collection.json")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
