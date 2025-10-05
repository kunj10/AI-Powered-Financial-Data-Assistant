"""Main FastAPI application entry point."""

import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from services import VectorSearchService, TransactionSummarizer, LLMSummarizer
from api.routes import search, summary, transactions

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_TITLE,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
search_service = VectorSearchService()
rule_summarizer = TransactionSummarizer()
llm_summarizer = None

# Try to initialize LLM summarizer
try:
    llm_summarizer = LLMSummarizer()
    print("✅ Gemini LLM initialized successfully")
except Exception as e:
    print(f"⚠️  LLM Summarizer not available: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    print("\n🚀 Starting AI Financial Data Assistant API...")
    
    # Initialize search service
    try:
        # The pickle file is named transactions.pkl in the same directory as the FAISS index
        import os
        embeddings_dir = os.path.dirname(settings.VECTOR_DB_PATH)
        transactions_pkl_path = os.path.join(embeddings_dir, 'transactions.pkl')
        
        search_service.initialize(
            index_path=settings.VECTOR_DB_PATH,
            transactions_path=transactions_pkl_path
        )
        print("✅ Search service initialized successfully")
        
        # Inject services into routes
        search.set_search_service(search_service)
        transactions.set_search_service(search_service)
        summary.set_services(search_service, rule_summarizer, llm_summarizer)
        
    except Exception as e:
        print(f"❌ Error initializing search service: {e}")
        search_service.is_ready = False


# Health check endpoint
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "AI Financial Data Assistant API is running",
        "version": settings.APP_VERSION,
        "services": {
            "search": search_service.is_ready,
            "llm": llm_summarizer is not None
        }
    }


# Include routers
app.include_router(search.router)
app.include_router(transactions.router)
app.include_router(summary.router)


if __name__ == "__main__":
    import uvicorn
    
    # Display localhost for user convenience (server still binds to 0.0.0.0)
    display_host = "localhost" if settings.API_HOST == "0.0.0.0" else settings.API_HOST
    
    print(f"\n🚀 Starting server on http://{display_host}:{settings.API_PORT}")
    print(f"📚 API Documentation: http://{display_host}:{settings.API_PORT}/docs")
    print(f"📊 ReDoc: http://{display_host}:{settings.API_PORT}/redoc\n")
    
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
