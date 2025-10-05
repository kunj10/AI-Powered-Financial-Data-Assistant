"""Summary and analytics endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api", tags=["Analytics"])

# Will be injected from main.py
search_service = None
rule_summarizer = None
llm_summarizer = None


class SummarizeRequest(BaseModel):
    """Request model for transaction summarization."""
    limit: int = Field(100, ge=1, le=500, description="Number of transactions to summarize")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    category: Optional[str] = Field(None, description="Filter by category")


class AskRequest(BaseModel):
    """Request model for AI question answering."""
    question: str = Field(..., description="Question about transactions")
    context_limit: int = Field(50, ge=1, le=200, description="Number of transactions for context")


@router.post("/summary")
async def get_summary(request: SummarizeRequest):
    """
    Get rule-based statistical summary of transactions.
    
    Provides detailed breakdown by category, user, payment method, etc.
    """
    if not search_service or not search_service.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Get transactions
        if request.user_id:
            transactions = search_service.get_user_transactions(request.user_id, request.limit)
        elif request.category:
            transactions = search_service.get_category_transactions(request.category, request.limit)
        else:
            transactions = search_service.embedding_service.transactions[:request.limit]
        
        # Generate summary
        summary = rule_summarizer.summarize_transactions(transactions)
        text_summary = rule_summarizer.generate_text_summary(transactions)
        
        return {
            "summary": summary,
            "text_summary": text_summary,
            "transaction_count": len(transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize")
async def ai_summarize(request: SummarizeRequest):
    """
    Get AI-powered summary using Google Gemini.
    
    Provides natural language insights and recommendations.
    """
    if not llm_summarizer:
        raise HTTPException(
            status_code=503,
            detail="LLM service not available. Please set GOOGLE_API_KEY."
        )
    
    if not search_service or not search_service.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Get transactions
        if request.user_id:
            transactions = search_service.get_user_transactions(request.user_id, request.limit)
        elif request.category:
            transactions = search_service.get_category_transactions(request.category, request.limit)
        else:
            transactions = search_service.embedding_service.transactions[:request.limit]
        
        # Generate AI summary
        summary = llm_summarizer.summarize_transactions(transactions)
        
        return {
            "summary": summary,
            "transaction_count": len(transactions),
            "model": "models/gemini-1.5-flash"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask")
async def ask_question(request: AskRequest):
    """
    Ask questions about transactions using AI.
    
    Provides intelligent answers based on transaction data.
    """
    if not llm_summarizer:
        raise HTTPException(
            status_code=503,
            detail="LLM service not available. Please set GOOGLE_API_KEY."
        )
    
    if not search_service or not search_service.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Get recent transactions for context
        transactions = search_service.embedding_service.transactions[:request.context_limit]
        
        # Get AI answer 
        answer = llm_summarizer.answer_question(transactions, request.question)
        
        return {
            "question": request.question,
            "answer": answer,
            "context_size": len(transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def set_services(search_svc, rule_sum, llm_sum):
    """Set the service instances."""
    global search_service, rule_summarizer, llm_summarizer
    search_service = search_svc
    rule_summarizer = rule_sum
    llm_summarizer = llm_sum
