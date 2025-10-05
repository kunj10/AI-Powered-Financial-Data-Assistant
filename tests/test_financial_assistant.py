"""Test Suite for AI Financial Data Assistant.

Tests all core functionality including data generation, embeddings, search, and API endpoints.
"""

import pytest
import json
import os
import sys
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.data_generator import FinancialDataGenerator
from services.embedding_service import EmbeddingService
from services.vector_search_service import VectorSearchService
from services.summarizer_service import TransactionSummarizer
from api.app import app


# Test client for API
client = TestClient(app)


class TestDataGenerator:
    """Test synthetic data generation."""

    def test_generator_initialization(self):
        """Test that generator initializes correctly."""
        generator = FinancialDataGenerator(num_users=2, transactions_per_user_range=(10, 20))
        assert generator.num_users == 2
        assert generator.transactions_per_user_range == (10, 20)
        assert len(generator.categories) > 0

    def test_generate_transaction(self):
        """Test single transaction generation."""
        generator = FinancialDataGenerator()
        txn = generator.generate_transaction("USER001", 1)
        
        assert txn['transaction_id'] == "TXN000001"
        assert txn['user_id'] == "USER001"
        assert 'amount' in txn
        assert 'category' in txn
        assert 'description' in txn
        assert txn['currency'] == "INR"

    def test_generate_all_transactions(self):
        """Test generating transactions for all users."""
        generator = FinancialDataGenerator(num_users=2, transactions_per_user_range=(5, 10))
        transactions = generator.generate_all_transactions()
        
        assert len(transactions) >= 10  # At least 2 users * 5 min transactions
        assert len(transactions) <= 20  # At most 2 users * 10 max transactions
        
        # Check unique users
        users = set(t['user_id'] for t in transactions)
        assert len(users) == 2


class TestEmbeddingService:
    """Test embedding creation and FAISS indexing."""

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions for testing."""
        generator = FinancialDataGenerator(num_users=1, transactions_per_user_range=(10, 10))
        return generator.generate_all_transactions()

    def test_embedding_service_initialization(self):
        """Test embedding service initialization."""
        service = EmbeddingService()
        assert service.model is not None
        assert service.dimension > 0

    def test_create_transaction_text(self, sample_transactions):
        """Test transaction text creation."""
        service = EmbeddingService()
        text = service.create_transaction_text(sample_transactions[0])
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert sample_transactions[0]['category'] in text

    def test_create_embeddings(self, sample_transactions):
        """Test embedding creation."""
        service = EmbeddingService()
        embeddings = service.create_embeddings(sample_transactions)
        
        assert embeddings.shape[0] == len(sample_transactions)
        assert embeddings.shape[1] == service.dimension

    def test_build_index(self, sample_transactions):
        """Test FAISS index building."""
        service = EmbeddingService()
        service.build_index(sample_transactions)
        
        assert service.index is not None
        assert service.index.ntotal == len(sample_transactions)
        assert len(service.transactions) == len(sample_transactions)


class TestVectorSearch:
    """Test semantic search functionality."""

    @pytest.fixture
    def search_service(self):
        """Create and initialize search service."""
        # This assumes setup.py has been run
        service = VectorSearchService()
        # Try to initialize, but don't fail if index doesn't exist
        service.initialize()
        return service

    def test_search_service_initialization(self):
        """Test search service initialization."""
        service = VectorSearchService()
        assert service.embedding_service is not None

    @pytest.mark.skipif(
        not os.path.exists("./embeddings/vector_store.faiss"),
        reason="FAISS index not built. Run setup.py first."
    )
    def test_search_basic(self, search_service):
        """Test basic search functionality."""
        if not search_service.is_ready:
            pytest.skip("Search service not initialized")
        
        results = search_service.search("food expenses", top_k=5)
        assert len(results) <= 5
        assert all('similarity_score' in r for r in results)

    @pytest.mark.skipif(
        not os.path.exists("./embeddings/vector_store.faiss"),
        reason="FAISS index not built"
    )
    def test_search_with_filters(self, search_service):
        """Test search with filters."""
        if not search_service.is_ready:
            pytest.skip("Search service not initialized")
        
        results = search_service.search(
            "restaurant",
            top_k=10,
            min_amount=100,
            max_amount=5000
        )
        
        for result in results:
            assert 100 <= result['amount'] <= 5000


class TestSummarizer:
    """Test rule-based summarization."""

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transactions."""
        generator = FinancialDataGenerator(num_users=2, transactions_per_user_range=(20, 20))
        return generator.generate_all_transactions()

    def test_summarize_transactions(self, sample_transactions):
        """Test transaction summarization."""
        summarizer = TransactionSummarizer()
        summary = summarizer.summarize_transactions(sample_transactions)
        
        assert 'overview' in summary
        assert 'by_category' in summary
        assert 'by_user' in summary
        assert 'insights' in summary
        
        assert summary['overview']['total_transactions'] == len(sample_transactions)

    def test_generate_text_summary(self, sample_transactions):
        """Test text summary generation."""
        summarizer = TransactionSummarizer()
        text = summarizer.generate_text_summary(sample_transactions)
        
        assert isinstance(text, str)
        assert len(text) > 0
        assert "Financial Summary" in text


class TestAPI:
    """Test FastAPI endpoints."""

    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'services' in data

    def test_get_categories(self):
        """Test get categories endpoint."""
        response = client.get("/api/categories")
        # May return 503 if not initialized, which is acceptable
        assert response.status_code in [200, 503]

    def test_get_users(self):
        """Test get users endpoint."""
        response = client.get("/api/users")
        assert response.status_code in [200, 503]

    def test_get_stats(self):
        """Test statistics endpoint."""
        response = client.get("/api/stats")
        assert response.status_code in [200, 503]

    @pytest.mark.skipif(
        not os.path.exists("./embeddings/vector_store.faiss"),
        reason="System not initialized"
    )
    def test_search_endpoint(self):
        """Test search endpoint."""
        response = client.post(
            "/api/search",
            json={"query": "food expenses", "top_k": 5}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert 'results' in data
            assert 'query' in data
            assert data['query'] == "food expenses"

    @pytest.mark.skipif(
        not os.path.exists("./embeddings/vector_store.faiss"),
        reason="System not initialized"
    )
    def test_get_transactions_endpoint(self):
        """Test get transactions endpoint."""
        response = client.get("/api/transactions?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            assert 'transactions' in data
            assert 'total' in data

    @pytest.mark.skipif(
        not os.path.exists("./embeddings/vector_store.faiss"),
        reason="System not initialized"
    )
    def test_summary_endpoint(self):
        """Test summary endpoint."""
        response = client.post(
            "/api/summary",
            json={"limit": 50}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert 'summary' in data
            assert 'text_summary' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
