"""Transaction management endpoints."""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/api", tags=["Transactions"])

# Will be injected from main.py
search_service = None


@router.get("/transactions")
async def get_transactions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of transactions"),
    offset: int = Query(0, ge=0, description="Number of transactions to skip (for pagination)")
):
    """Get transactions with optional filters and pagination support."""
    if not search_service or not search_service.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        # Get all matching transactions
        if user_id:
            all_transactions = search_service.get_user_transactions(user_id, limit=1000)
        elif category:
            all_transactions = search_service.get_category_transactions(category, limit=1000)
        else:
            all_transactions = search_service.embedding_service.transactions
        
        # Apply pagination
        total_count = len(all_transactions)
        paginated_transactions = all_transactions[offset:offset + limit]
        
        return {
            "total": total_count,
            "count": len(paginated_transactions),
            "offset": offset,
            "limit": limit,
            "has_more": (offset + limit) < total_count,
            "transactions": paginated_transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_categories():
    """Get list of all transaction categories."""
    if not search_service or not search_service.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        transactions = search_service.embedding_service.transactions
        categories = sorted(set(t.get('category', 'Unknown') for t in transactions))
        
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def get_users():
    """Get list of all users in the system."""
    if not search_service or not search_service.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        transactions = search_service.embedding_service.transactions
        users = sorted(set(t.get('user_id', 'Unknown') for t in transactions))
        
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_statistics():
    """Get overall transaction statistics."""
    if not search_service or not search_service.is_ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    try:
        stats = search_service.get_transaction_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def set_search_service(service):
    """Set the search service instance."""
    global search_service
    search_service = service
