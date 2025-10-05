"""Search endpoints for semantic and filtered search."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

router = APIRouter(prefix="/api", tags=["Search"])

# Will be injected from main.py
search_service = None


class SearchRequest(BaseModel):
    """Request model for transaction search."""
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(10, ge=1, le=100, description="Number of results to return")
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    category: Optional[str] = Field(None, description="Filter by category")
    min_amount: Optional[float] = Field(None, description="Minimum transaction amount")
    max_amount: Optional[float] = Field(None, description="Maximum transaction amount")


@router.post("/search")
async def search_transactions(request: SearchRequest):
    """
    Search transactions using natural language query.
    
    Returns semantically similar transactions based on the query.
    """
    if not search_service or not search_service.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Search service not ready. Please run setup.py to initialize the system."
        )
    
    try:
        results = search_service.search(
            query=request.query,
            top_k=request.top_k,
            user_id=request.user_id,
            category=request.category,
            min_amount=request.min_amount,
            max_amount=request.max_amount
        )
        
        return {
            "query": request.query,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def set_search_service(service):
    """Set the search service instance."""
    global search_service
    search_service = service
