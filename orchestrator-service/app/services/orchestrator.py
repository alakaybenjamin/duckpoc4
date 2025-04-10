from typing import Dict, List, Optional
from .search_service import SearchService
from .user_history_service import UserHistoryService
from app.models.schemas import SearchRequest, SaveSearchRequest, SearchResponse
from fastapi import HTTPException, Request
from opentelemetry import trace
from opentelemetry.trace.status import Status, StatusCode
import logging
import traceback

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class OrchestratorService:
    """
    Orchestrator service that coordinates between microservices
    """
    def __init__(self, search_service: SearchService, user_history_service: UserHistoryService):
        self.search_service = search_service
        self.user_history_service = user_history_service
    
    async def process_search(self, request: Request, user_id: str = None) -> SearchResponse:
        """
        Process a search request:
        1. Forward the raw request to Search Service
        2. Record the search in history if user_id provided
        3. Return combined results
        """
        try:
            # Step 1: Forward the raw request to search service
            with tracer.start_as_current_span("search_service.search") as search_span:
                logger.info("Forwarding raw search request to search service")
                search_results = await self.search_service.search(request)
                search_span.set_attribute("search.results.count", search_results.get("count", 0))
                search_span.set_status(Status(StatusCode.OK))
                logger.info(f"Search results received: {search_results}")
            
            # Step 2: Record search history if user_id is provided
            search_id = None
            if user_id:
                with tracer.start_as_current_span("user_history.record_search") as history_span:
                    try:
                        logger.info(f"Recording search history for user: {user_id}")
                        # Extract search text from the raw request for history
                        raw_body = await request.json()
                        search_text = raw_body.get("search", {}).get("text", "")
                        search_fields = raw_body.get("search", {}).get("fields", [])
                        
                        history_span.set_attribute("user.id", user_id)
                        history_span.set_attribute("search.text", search_text)
                        
                        history_data = await self.user_history_service.record_search(
                            user_id=user_id,
                            search_text=search_text,
                            search_fields=search_fields
                        )
                        search_id = history_data.get("id")
                        history_span.set_attribute("search.history.id", search_id)
                        history_span.set_status(Status(StatusCode.OK))
                        logger.info(f"Search history recorded with ID: {search_id}")
                    except Exception as e:
                        # Log the error but don't fail the request
                        history_span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                        history_span.set_attribute("error.type", "history_error")
                        history_span.set_attribute("error.message", str(e))
                        logger.error(f"Failed to record search history: {str(e)}\n{traceback.format_exc()}")
            
            # Step 3: Return combined results
            response = SearchResponse(
                status=search_results.get("status", "success"),
                count=search_results.get("count", 0),
                results=search_results.get("results", []),
                search_id=search_id
            )
            logger.info(f"Returning search response: {response.dict()}")
            return response
            
        except HTTPException as e:
            # Re-raise HTTP exceptions
            logger.error(f"HTTP error in process_search: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Error processing search request: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)
    
    async def save_search(self, request: SaveSearchRequest) -> Dict:
        """
        Save a search with a name
        """
        try:
            logger.info(f"Saving search with ID {request.search_id} for user {request.user_id}")
            response = await self.user_history_service.save_search(
                user_id=request.user_id,
                search_id=request.search_id,
                search_name=request.search_name
            )
            logger.info(f"Search saved successfully: {response}")
            return response
        except HTTPException as e:
            logger.error(f"HTTP error in save_search: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Error saving search: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg)
    
    async def get_user_search_history(self, user_id: str, saved: Optional[bool] = None) -> List[Dict]:
        """
        Get search history for a user
        """
        try:
            logger.info(f"Retrieving search history for user {user_id} (saved={saved})")
            response = await self.user_history_service.get_user_search_history(user_id, saved)
            logger.info(f"Retrieved {len(response)} history entries")
            return response
        except HTTPException as e:
            logger.error(f"HTTP error in get_user_search_history: {str(e)}")
            raise
        except Exception as e:
            error_msg = f"Error retrieving search history: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=error_msg) 