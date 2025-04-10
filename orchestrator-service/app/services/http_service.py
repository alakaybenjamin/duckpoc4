import httpx
from typing import Dict, Optional
from fastapi import HTTPException
from .interfaces import ServiceInterface
import logging
import json

logger = logging.getLogger(__name__)

class HttpService(ServiceInterface):
    """
    HTTP service implementation
    """
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def call_service(
        self, 
        endpoint: str, 
        method: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """
        Call a service endpoint using HTTP
        
        Args:
            endpoint: The endpoint to call
            method: The HTTP method to use
            data: Optional request body data
            headers: Optional request headers
        """
        url = f"{self.base_url}{endpoint}"
        
        # Ensure headers is a dict
        headers = headers or {}
        
        # Log request details
        logger.info(f"Making {method} request to {url}")
        logger.info(f"Request headers: {headers}")
        logger.info(f"Request data: {data}")
        
        async with httpx.AsyncClient() as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    # Let httpx handle the JSON serialization
                    response = await client.post(url, json=data, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, 
                                   detail=f"Service error: {response.text}")
                
                return response.json()
                
            except httpx.RequestError as e:
                logger.error(f"Request error details: {str(e)}")
                raise HTTPException(status_code=500, 
                               detail=f"Service communication error: {str(e)}") 