"""Integration Tests for AI Financial Data Assistant.

Tests the complete workflow from data generation to API responses.
"""

import pytest
import os
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.data_generator import FinancialDataGenerator
from services.embedding_service import EmbeddingService
from services.vector_search_service import VectorSearchService
from services.summarizer_service import TransactionSummarizer


class TestFullWorkflow:
    """Test the complete end-to-end workflow."""

    @pytest.fixture(scope="class")
    def temp_data_dir(self, tmp_path_factory):
        """Create temporary directory for test data."""
        return tmp_path_factory.mktemp("test_data")

    @pytest.fixture(scope="class")
    def generated_transactions(self, temp_data_dir):
        """Generate test transactions."""
        generator = FinancialDataGenerator(
            num_users=2,
            transactions_per_user_range=(20, 30)
        )
        transactions = generator.generate_all_transactions()
        
        # Save to temp directory
        data_file = temp_data_dir / "transactions.json"
        with open(data_file, 'w') as f:
            json.dump(transactions, f)
        
        return transactions, str(data_file)

    @pytest.fixture(scope="class")
    def built_index(self, temp_data_dir, generated_transactions):
        """Build FAISS index from generated transactions."""
        transactions, _ = generated_transactions
        
        # Create embedding service
        service = EmbeddingService()
        service.build_index(transactions)
        
        # Save to temp directory
        index_path = str(temp_data_dir / "test_index.faiss")
        pkl_path = str(temp_data_dir / "test_transactions.pkl")
        service.save_index(index_path, pkl_path)
        
        return service, index_path, pkl_path

    def test_01_data_generation(self, generated_transactions):
        """Test that data generation produces valid transactions."""
        transactions, data_file = generated_transactions
        
        # Verify transactions were generated
        assert len(transactions) >= 40  # 2 users * 20 min
        assert len(transactions) <= 60  # 2 users * 30 max
        
        # Verify file was created
        assert os.path.exists(data_file)
        
        # Verify transaction structure
        for txn in transactions[:5]:
            assert 'transaction_id' in txn
            assert 'user_id' in txn
            assert 'amount' in txn
            assert 'category' in txn
            assert 'description' in txn
            assert txn['currency'] == 'INR'
        
        # Verify users
        users = set(t['user_id'] for t in transactions)
        assert len(users) == 2
        
        print(f"✅ Generated {len(transactions)} transactions for {len(users)} users")

    def test_02_embedding_creation(self, built_index):
        """Test that embeddings are created correctly."""
        service, index_path, pkl_path = built_index
        
        # Verify index was built
        assert service.index is not None
        assert service.index.ntotal > 0
        
        # Verify files were created
        assert os.path.exists(index_path)
        assert os.path.exists(pkl_path)
        
        print(f"✅ Built FAISS index with {service.index.ntotal} vectors")

    def test_03_index_persistence(self, temp_data_dir, built_index):
        """Test that index can be saved and loaded."""
        _, index_path, pkl_path = built_index
        
        # Create new service and load index
        new_service = EmbeddingService()
        new_service.load_index(index_path, pkl_path)
        
        # Verify loaded correctly
        assert new_service.index is not None
        assert new_service.index.ntotal > 0
        assert len(new_service.transactions) > 0
        
        print(f"✅ Successfully loaded index with {new_service.index.ntotal} vectors")

    def test_04_semantic_search(self, built_index):
        """Test semantic search functionality."""
        service, _, _ = built_index
        
        # Perform search
        query = "food and restaurant expenses"
        results = service.search(query, top_k=5)
        
        # Verify results
        assert len(results) > 0
        assert len(results) <= 5
        
        # Verify result structure
        for result in results:
            assert 'similarity_score' in result
            assert 'distance' in result
            assert 'description' in result
            assert result['similarity_score'] > 0
        
        print(f"✅ Search returned {len(results)} results")

    def test_05_filtered_search(self, temp_data_dir, built_index):
        """Test search with filters."""
        _, index_path, pkl_path = built_index
        
        # Create search service
        search_service = VectorSearchService()
        search_service.embedding_service.load_index(index_path, pkl_path)
        search_service.is_ready = True
        
        # Search with amount filter
        results = search_service.search(
            query="shopping",
            top_k=10,
            min_amount=100,
            max_amount=5000
        )
        
        # Verify filters applied
        for result in results:
            assert 100 <= result['amount'] <= 5000
        
        print(f"✅ Filtered search returned {len(results)} results")

    def test_06_summarization(self, generated_transactions):
        """Test transaction summarization."""
        transactions, _ = generated_transactions
        
        # Create summarizer
        summarizer = TransactionSummarizer()
        
        # Generate summary
        summary = summarizer.summarize_transactions(transactions)
        
        # Verify summary structure
        assert 'overview' in summary
        assert 'by_category' in summary
        assert 'by_user' in summary
        assert 'insights' in summary
        
        # Verify overview
        assert summary['overview']['total_transactions'] == len(transactions)
        assert 'total_debit' in summary['overview']
        assert 'total_credit' in summary['overview']
        
        # Generate text summary
        text_summary = summarizer.generate_text_summary(transactions)
        assert isinstance(text_summary, str)
        assert len(text_summary) > 0
        
        print(f"✅ Generated summary for {len(transactions)} transactions")

    def test_07_user_filtering(self, temp_data_dir, built_index):
        """Test user-specific filtering."""
        _, index_path, pkl_path = built_index
        
        # Create search service
        search_service = VectorSearchService()
        search_service.embedding_service.load_index(index_path, pkl_path)
        search_service.is_ready = True
        
        # Get all users
        all_transactions = search_service.embedding_service.transactions
        users = set(t['user_id'] for t in all_transactions)
        
        # Test each user
        for user_id in users:
            user_txns = search_service.get_user_transactions(user_id, limit=100)
            
            # Verify all transactions belong to user
            for txn in user_txns:
                assert txn['user_id'] == user_id
            
            print(f"✅ User {user_id} has {len(user_txns)} transactions")

    def test_08_category_filtering(self, temp_data_dir, built_index):
        """Test category-specific filtering."""
        _, index_path, pkl_path = built_index
        
        # Create search service
        search_service = VectorSearchService()
        search_service.embedding_service.load_index(index_path, pkl_path)
        search_service.is_ready = True
        
        # Get all categories
        all_transactions = search_service.embedding_service.transactions
        categories = set(t['category'] for t in all_transactions)
        
        # Test a few categories
        for category in list(categories)[:3]:
            cat_txns = search_service.get_category_transactions(category, limit=100)
            
            # Verify all transactions belong to category
            for txn in cat_txns:
                assert txn['category'] == category
            
            print(f"✅ Category '{category}' has {len(cat_txns)} transactions")

    def test_09_statistics(self, temp_data_dir, built_index):
        """Test statistics generation."""
        _, index_path, pkl_path = built_index
        
        # Create search service
        search_service = VectorSearchService()
        search_service.embedding_service.load_index(index_path, pkl_path)
        search_service.is_ready = True
        
        # Get statistics
        stats = search_service.get_transaction_stats()
        
        # Verify stats structure
        assert 'total_transactions' in stats
        assert 'total_users' in stats
        assert 'categories' in stats
        assert 'total_amount' in stats
        assert 'total_debit' in stats
        assert 'total_credit' in stats
        
        # Verify values make sense
        assert stats['total_transactions'] > 0
        assert stats['total_users'] > 0
        assert len(stats['categories']) > 0
        
        print(f"✅ Statistics: {stats['total_transactions']} transactions, {stats['total_users']} users")

    def test_10_complete_workflow(self, temp_data_dir):
        """Test the complete workflow from start to finish."""
        print("\n" + "="*60)
        print("COMPLETE WORKFLOW TEST")
        print("="*60)
        
        # Step 1: Generate data
        print("\n1. Generating data...")
        generator = FinancialDataGenerator(num_users=2, transactions_per_user_range=(15, 20))
        transactions = generator.generate_all_transactions()
        print(f"   ✅ Generated {len(transactions)} transactions")
        
        # Step 2: Create embeddings
        print("\n2. Creating embeddings...")
        embedding_service = EmbeddingService()
        embedding_service.build_index(transactions)
        print(f"   ✅ Built index with {embedding_service.index.ntotal} vectors")
        
        # Step 3: Save index
        print("\n3. Saving index...")
        index_path = str(temp_data_dir / "workflow_index.faiss")
        pkl_path = str(temp_data_dir / "workflow_transactions.pkl")
        embedding_service.save_index(index_path, pkl_path)
        print(f"   ✅ Saved index to disk")
        
        # Step 4: Load index
        print("\n4. Loading index...")
        new_service = EmbeddingService()
        new_service.load_index(index_path, pkl_path)
        print(f"   ✅ Loaded index with {new_service.index.ntotal} vectors")
        
        # Step 5: Perform search
        print("\n5. Performing semantic search...")
        results = new_service.search("food expenses", top_k=3)
        print(f"   ✅ Found {len(results)} results")
        
        # Step 6: Generate summary
        print("\n6. Generating summary...")
        summarizer = TransactionSummarizer()
        summary = summarizer.summarize_transactions(transactions)
        print(f"   ✅ Generated summary with {len(summary)} sections")
        
        print("\n" + "="*60)
        print("✅ COMPLETE WORKFLOW TEST PASSED")
        print("="*60 + "\n")
        
        # Final assertions
        assert len(transactions) > 0
        assert embedding_service.index.ntotal > 0
        assert len(results) > 0
        assert 'overview' in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
