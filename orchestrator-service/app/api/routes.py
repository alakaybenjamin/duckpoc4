from fastapi import APIRouter, HTTPException, Depends, Request, Header, Body
from typing import List, Dict, Any, Optional
from app.models.schemas import SearchRequest, SaveSearchRequest, SearchResponse
from app.services.factory import get_search_service, get_user_history_service
from app.services.orchestrator import OrchestratorService
from app.core.config import tracer
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode
import logging
import traceback
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# Dependency injection
def get_orchestrator_service():
    search_service = get_search_service()
    user_history_service = get_user_history_service()
    return OrchestratorService(search_service, user_history_service)

@router.post("/search", response_model=SearchResponse)
async def search(
    request: Request,
    body: Dict[str, Any] = Body(..., example={"search_text": "nice", "search_fields": ["hotelName", "description"]}),
    user_id: str = Header(..., description="User ID for tracking search history", alias="user_id"),
    orchestrator: OrchestratorService = Depends(get_orchestrator_service)
):
    """
    Execute a search and optionally record in history
    
    The search request should contain:
    - search_text: The text to search for (required)
    - search_fields: List of fields to search in (optional, default: ["hotelName", "description", "category"])
    - select: List of fields to return (optional, default: ["hotelId", "hotelName", "description", "category"])
    """
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    
    # Get the current span (created by FastAPI instrumentation)
    current_span = trace.get_current_span()
    current_span.set_attribute("request.id", request_id)
    current_span.set_attribute("user.id", user_id)
    current_span.set_attribute("search.text", body.get("search_text", ""))
    
    try:
        # Log the start of the request
        logger.info(f"Starting search request {request_id} from user: {user_id}")
        
        # Process the search request
        response = await orchestrator.process_search(request, user_id)
        
        # Add response metadata to the span
        current_span.set_attribute("search.results.count", response.count)
        current_span.set_attribute("search.id", response.search_id or "none")
        current_span.set_status(Status(StatusCode.OK))
        
        logger.info(f"Search request {request_id} completed successfully")
        return response
        
    except HTTPException as e:
        # Add error information to the span
        current_span.set_status(
            Status(StatusCode.ERROR, f"HTTP {e.status_code}: {e.detail}")
        )
        current_span.set_attribute("error.type", "http_error")
        current_span.set_attribute("error.code", e.status_code)
        current_span.set_attribute("error.message", str(e.detail))
        
        logger.error(f"HTTP error during search request {request_id}: {str(e)}")
        raise
        
    except Exception as e:
        # Add error information to the span
        current_span.set_status(
            Status(StatusCode.ERROR, str(e))
        )
        current_span.set_attribute("error.type", "unexpected_error")
        current_span.set_attribute("error.message", str(e))
        
        error_msg = f"Unexpected error during search request {request_id}: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/search/save", response_model=Dict[str, Any])
async def save_search(
    request: SaveSearchRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service)
):
    """
    Save a search with a name
    """
    try:
        logger.info(f"Received save search request: {request.dict()}")
        response = await orchestrator.save_search(request)
        logger.info(f"Search saved successfully: {response}")
        return response
    except HTTPException as e:
        logger.error(f"HTTP error during save search: {str(e)}")
        raise
    except Exception as e:
        error_msg = f"Unexpected error during save search: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/history/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_history(
    user_id: str,
    saved: Optional[bool] = None,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service)
):
    """
    Get search history for a user
    """
    try:
        logger.info(f"Retrieving search history for user {user_id} (saved={saved})")
        response = await orchestrator.get_user_search_history(user_id, saved)
        logger.info(f"Retrieved {len(response)} history entries")
        return response
    except HTTPException as e:
        logger.error(f"HTTP error during history retrieval: {str(e)}")
        raise
    except Exception as e:
        error_msg = f"Unexpected error during history retrieval: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_msg) 