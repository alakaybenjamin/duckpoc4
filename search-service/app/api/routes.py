from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import SearchRequest, SearchResponse
from app.services.search_provider import SearchProvider
from typing import Callable

router = APIRouter(prefix="/api")

def get_search_provider():
    return SearchProvider.get_provider("azure")

@router.post("/search", response_model=SearchResponse)
async def search(
    request: SearchRequest, 
    search_provider: SearchProvider = Depends(get_search_provider)
):
    try:
        # Execute search using provider
        results = await search_provider.search(
            search_text=request.search_text,
            search_fields=request.search_fields,
            select=request.select
        )
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 