from typing import Dict
from fastapi import Request
from .interfaces import ServiceInterface
import logging
import json

logger = logging.getLogger(__name__)

class SearchService:
    """
    Search service client
    """
    def __init__(self, service: ServiceInterface):
        self.service = service
    
    async def search(self, request: Request) -> Dict:
        """
        Forward search request to the search service
        """
        # Get the raw request body
        raw_body = await request.json()
        logger.info(f"Received raw request body: {raw_body}")
        
        # Create a new headers dict with only the necessary headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "user_id": request.headers.get("user_id", "")
        }
        
        logger.info(f"Forwarding headers: {headers}")
        
        # Convert the body to a string to ensure proper serialization
        json_body = json.dumps(raw_body)
        logger.info(f"Serialized request body: {json_body}")
        
        return await self.service.call_service("/api/search", "POST", raw_body, headers) 