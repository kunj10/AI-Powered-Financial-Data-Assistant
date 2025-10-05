# 📁 Project Structure & Architecture

**AI-Powered Financial Data Assistant** - Detailed architecture documentation.

---

## 🏗️ Architecture Overview

This project follows a **layered architecture** pattern with clear separation of concerns.

```
┌─────────────┐
│   Client    │ (Browser, Postman, cURL)
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  ┌─────────┐ ┌─────────┐ ┌────────┐│
│  │ Search  │ │ Summary │ │ Txns   ││
│  └─────────┘ └─────────┘ └────────┘│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       Service Layer (Business)      │
│  ┌──────────┐ ┌──────────┐ ┌──────┐│
│  │  Vector  │ │Summarizer│ │ LLM  ││
│  │  Search  │ │ Service  │ │ AI   ││
│  └──────────┘ └──────────┘ └──────┘│
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│          Data Layer                 │
│  ┌──────────┐ ┌──────────┐         │
│  │  FAISS   │ │   JSON   │         │
│  │  Index   │ │   Data   │         │
│  └──────────┘ └──────────┘         │
└─────────────────────────────────────┘
```

---

## 📂 Directory Structure

```
financial-data-assistant/
├── api/
│   ├── app.py                      # Main FastAPI application
│   └── routes/                     # Modular endpoints
│       ├── search.py               # Semantic search
│       ├── summary.py              # Analytics & AI
│       └── transactions.py         # Transaction management
│
├── services/
│   ├── data_generator.py           # Synthetic data (Faker)
│   ├── embedding_service.py        # Vector embeddings
│   ├── vector_search_service.py    # FAISS search
│   ├── summarizer_service.py       # Rule-based analytics
│   └── llm_summarizer_service.py   # AI summaries (Gemini)
│
├── config/
│   └── settings.py                 # Configuration
│
├── tests/
│   ├── test_financial_assistant.py # Unit tests
│   └── test_integration.py         # Integration tests
│
├── data/
│   └── transactions.json           # Generated data
│
├── embeddings/
│   ├── vector_store.faiss          # FAISS index
│   └── transactions.pkl            # Metadata
│
├── examples/
│   └── FinancialDataAssistant.postman_collection.json
│
├── .env.example                    # Config template
├── requirements.txt                # Dependencies
├── setup.py                        # Initialization
└── README.md                       # Documentation
```

---

## 🔄 Data Flow

### 1. Setup Phase
```
setup.py
   ↓
data_generator.py → transactions.json
   ↓
embedding_service.py → vector_store.faiss + transactions.pkl
```

### 2. API Request Flow
```
Client Request
   ↓
API Routes (search.py, summary.py, transactions.py)
   ↓
Service Layer (vector_search_service.py, llm_summarizer_service.py)
   ↓
Data Layer (FAISS index, JSON data)
   ↓
Response to Client
```

---

## 📦 Component Details

### API Layer (`api/`)
- **app.py** - FastAPI application with lifespan management
- **routes/** - Modular endpoint handlers
  - `search.py` - Semantic search with filters
  - `summary.py` - Analytics and AI summaries
  - `transactions.py` - Transaction CRUD operations

### Service Layer (`services/`)
- **data_generator.py** - Generates realistic financial transactions using Faker
- **embedding_service.py** - Creates 384-dim vectors using Sentence Transformers
- **vector_search_service.py** - FAISS-based semantic search
- **summarizer_service.py** - Rule-based statistical analysis
- **llm_summarizer_service.py** - AI-powered insights using Google Gemini

### Configuration (`config/`)
- **settings.py** - Centralized configuration from environment variables

### Tests (`tests/`)
- **test_financial_assistant.py** - Unit tests for services
- **test_integration.py** - End-to-end API tests

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|----------|
| **API** | FastAPI | REST API framework |
| **Vector DB** | FAISS | Similarity search |
| **Embeddings** | Sentence Transformers | Text to vectors |
| **LLM** | Google Gemini | AI summaries |
| **Data Gen** | Faker | Synthetic data |
| **Testing** | Pytest | Unit & integration tests |

---

## 🔐 Security Architecture

- Environment-based configuration (`.env`)
- API key management (not hardcoded)
- Input validation (Pydantic models)
- CORS middleware
- Secure defaults

---

## 📊 Performance Characteristics

| Operation | Performance | Notes |
|-----------|------------|-------|
| Data Generation | 2-3s | 500 transactions |
| Embedding Creation | 8-10s | 500 transactions |
| Index Build | <1s | 500 vectors |
| Search Query | 5-10ms | Top-10 results |
| API Response | 50-100ms | Including processing |
| AI Summary | 2-4s | Gemini API call |

---

## 🚀 Scalability

**Current Capacity:**
- Up to 100K transactions
- 3-5 concurrent users
- Single-server deployment

---

## ✅ Design Patterns

1. **Layered Architecture** - Clear separation of concerns
2. **Dependency Injection** - Services injected into routes
3. **Repository Pattern** - Data access abstraction
4. **Factory Pattern** - Service initialization
5. **Singleton Pattern** - Configuration management

---

**This architecture ensures maintainability, testability, and scalability for production deployment.**
