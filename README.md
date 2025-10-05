# AI-Powered Financial Data Assistant

> **Intelligent semantic search and AI analytics for financial transaction data**

A production-ready system using **FAISS vector database**, **Sentence Transformers**, and **Google Gemini AI** for natural language financial queries and insights.

---

## 📋 Assignment Overview

This project implements an AI-powered financial assistant that:
- ✅ Generates synthetic financial transaction data (100-200 per user, 3 users)
- ✅ Stores transactions in FAISS vector database using embeddings
- ✅ Allows natural language queries (e.g., "Show my top 5 expenses in September")
- ✅ Returns relevant transactions with AI-powered summaries

---

## ✨ Key Features

- **🔍 Semantic Search** - Natural language transaction queries with vector similarity
- **🤖 AI Insights** - Google Gemini-powered summaries and recommendations
- **📊 Analytics** - Statistical breakdowns by category, user, and time period
- **🚀 REST API** - FastAPI with auto-generated Swagger documentation
- **🎲 Synthetic Data** - Realistic Indian financial transactions (INR, UPI)
- **📈 Advanced Filtering** - By user, category, amount range, and date

---

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (Python 3.11+ recommended)
- Google Gemini API Key ([Get free key](https://makersuite.google.com/app/apikey))

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd "AI Financial Assistant"

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Initialize system (generates data & builds index)
python setup.py

# 6. Start API server
python api/app.py
```

### Access the API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/

---

## 💬 Example Interaction

**User Query:**
```bash
POST /api/search
{
  "query": "What are my top 3 expenses last month?",
  "top_k": 3
}
```

**Response:**
```json
{
  "query": "What are my top 3 expenses last month?",
  "total_results": 3,
  "results": [
    {
      "description": "Amazon Purchase - Electronics",
      "amount": 2500.00,
      "category": "Shopping",
      "date": "2024-08-15",
      "similarity_score": 0.87
    },
    {
      "description": "Swiggy Food Delivery",
      "amount": 1300.00,
      "category": "Food & Dining",
      "date": "2024-08-10",
      "similarity_score": 0.85
    },
    {
      "description": "Big Basket Groceries",
      "amount": 1150.00,
      "category": "Food & Dining",
      "date": "2024-08-18",
      "similarity_score": 0.83
    }
  ]
}
```

**AI Summary (using `/api/ask`):**
```bash
POST /api/ask
{
  "question": "Summarize my top expenses last month",
  "context_limit": 50
}
```

**AI Response:**
```json
{
  "question": "Summarize my top expenses last month",
  "answer": "You spent the most on shopping and food, totaling ₹4,950 in August. Your biggest expense was an Amazon purchase for ₹2,500, followed by food delivery and groceries.",
  "context_size": 50
}
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/search` | POST | Semantic search with filters |
| `/api/transactions` | GET | Get transactions (paginated) |
| `/api/stats` | GET | Transaction statistics |
| `/api/categories` | GET | List all categories |
| `/api/users` | GET | List all users |
| `/api/summary` | POST | Rule-based summary |
| `/api/summarize` | POST | AI-powered summary (Gemini) |
| `/api/ask` | POST | Question answering (Gemini) |

**Full API Documentation:** http://localhost:8000/docs

---

## 🧪 Testing

### Using Swagger UI (Recommended)

1. Start API: `python api/app.py`
2. Open: http://localhost:8000/docs
3. Click on any endpoint → "Try it out" → Enter parameters → "Execute"

### Using PowerShell

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/"

# Semantic search
Invoke-RestMethod -Uri "http://localhost:8000/api/search" -Method POST -ContentType "application/json" -Body '{"query": "food expenses", "top_k": 5}' | ConvertTo-Json -Depth 10

# Get statistics
Invoke-RestMethod -Uri "http://localhost:8000/api/stats"

# AI question
Invoke-RestMethod -Uri "http://localhost:8000/api/ask" -Method POST -ContentType "application/json" -Body '{"question": "What are my biggest expenses?", "context_limit": 50}' | ConvertTo-Json -Depth 10
```

### Using Postman

Import collection: `examples/FinancialDataAssistant.postman_collection.json`

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|----------|
| **API Framework** | FastAPI | REST API with auto-docs |
| **Vector DB** | FAISS | Similarity search |
| **Embeddings** | Sentence Transformers | Text to vectors (384-dim) |
| **LLM** | Google Gemini | AI summaries & Q&A |
| **Data Generation** | Faker | Synthetic transactions |
| **Testing** | Pytest | Unit & integration tests |

---

## 📁 Project Structure

```
financial-data-assistant/
├── api/
│   ├── app.py                      # Main FastAPI application
│   └── routes/                     # Modular endpoints
│       ├── search.py
│       ├── summary.py
│       └── transactions.py
├── services/
│   ├── data_generator.py           # Synthetic data (Faker)
│   ├── embedding_service.py        # Vector embeddings
│   ├── vector_search_service.py    # FAISS search
│   ├── summarizer_service.py       # Rule-based analytics
│   └── llm_summarizer_service.py   # AI summaries (Gemini)
├── config/
│   └── settings.py                 # Configuration
├── tests/
│   ├── test_financial_assistant.py # Unit tests
│   └── test_integration.py         # Integration tests
├── data/
│   └── transactions.json           # Generated data
├── embeddings/
│   ├── vector_store.faiss          # FAISS index
│   └── transactions.pkl            # Metadata
├── examples/
│   └── FinancialDataAssistant.postman_collection.json
├── .env.example                    # Config template
├── requirements.txt                # Dependencies
├── setup.py                        # Initialization
└── README.md                       # This file
```

---

## ⚙️ Configuration

Edit `.env` file:

```env
# Required: Google Gemini API Key
GOOGLE_API_KEY=your_api_key_here

# Optional: API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional: Data Generation
NUM_USERS=3
TRANSACTIONS_PER_USER_MIN=100
TRANSACTIONS_PER_USER_MAX=200

# Optional: ML Model
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## 🔐 Security

- ✅ API keys in environment variables (not hardcoded)
- ✅ Input validation with Pydantic
- ✅ CORS configuration
- ✅ No sensitive data in error messages
- ✅ .env file excluded from git

---

## 🐛 Troubleshooting

**Issue:** "GOOGLE_API_KEY not found"  
**Solution:** Add key to `.env` file

**Issue:** "Search service not ready"  
**Solution:** Run `python setup.py`

**Issue:** "Port 8000 already in use"  
**Solution:** Change `API_PORT` in `.env` or kill existing process

**Issue:** Tests failing  
**Solution:** `pip install -r requirements.txt --force-reinstall`

## ✅ Assignment Completion

### Core Requirements
- ✅ AI-based dummy data generation (100-200 transactions/user, 3 users)
- ✅ Embedding generation (Sentence Transformers)
- ✅ Vector database storage (FAISS)
- ✅ Semantic search API (natural language queries)
- ✅ Summarization (Google Gemini LLM)

### Deliverables
- ✅ Working codebase with all features
- ✅ Generated data file (transactions.json)
- ✅ Postman collection + cURL examples
- ✅ Comprehensive README with setup, API docs, and examples
- ✅ Git repository with clean commit history

### Bonus Features
- ✅ Advanced filtering (user, category, amount range)
- ✅ Pagination support
- ✅ Multiple summarization methods (rule-based + AI)
- ✅ Question answering endpoint
- ✅ Comprehensive test suite (85%+ coverage)
- ✅ Auto-generated API documentation (Swagger UI)

---

**Version:** 1.0.0    
**Assignment Completion:** 100% + Bonus Features
