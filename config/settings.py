"""Configuration settings for AI Financial Data Assistant."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    
    # Google Gemini API
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Embedding Model
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # Data Configuration
    NUM_USERS: int = int(os.getenv("NUM_USERS", 3))
    TRANSACTIONS_PER_USER_MIN: int = int(os.getenv("TRANSACTIONS_PER_USER_MIN", 100))
    TRANSACTIONS_PER_USER_MAX: int = int(os.getenv("TRANSACTIONS_PER_USER_MAX", 200))
    
    # File Paths
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./embeddings/vector_store.faiss")
    TRANSACTIONS_DATA_PATH: str = os.getenv("TRANSACTIONS_DATA_PATH", "./data/transactions.json")
    
    # Application Info
    APP_TITLE: str = "AI Financial Data Assistant"
    APP_DESCRIPTION: str = "Semantic search and AI-powered insights for financial transactions"
    APP_VERSION: str = "1.0.0"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings."""
        if not cls.GOOGLE_API_KEY:
            print("⚠️  Warning: GOOGLE_API_KEY not set. AI features will be disabled.")
            return False
        return True


# Global settings instance
settings = Settings()
