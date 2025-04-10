from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional
import json
import logging
import sys
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure AI Search configuration
SEARCH_SERVICE_ENDPOINT = os.getenv("SEARCH_SERVICE_ENDPOINT")
INDEX_NAME = os.getenv("INDEX_NAME")
ADMIN_KEY = os.getenv("ADMIN_KEY")

# Log environment variable status
logger.info("Environment variable status:")
logger.info(f"SEARCH_SERVICE_ENDPOINT is {'set' if SEARCH_SERVICE_ENDPOINT else 'not set'}")
logger.info(f"INDEX_NAME is {'set' if INDEX_NAME else 'not set'}")
logger.info(f"ADMIN_KEY is {'set' if ADMIN_KEY else 'not set'}")

# Validate configuration
if not all([SEARCH_SERVICE_ENDPOINT, INDEX_NAME, ADMIN_KEY]):
    logger.error("Missing required environment variables")
    raise ValueError("Missing required environment variables")

class SearchRequest(BaseModel):
    search_text: str
    search_fields: Optional[List[str]] = ["hotelName", "description", "category"]
    select: Optional[List[str]] = ["hotelId", "hotelName", "description", "category"]

async def forward_to_azure(request: SearchRequest):
    try:
        # Get query parameters
        params = {"api-version": "2023-11-01"}
        
        # Construct the Azure AI Search URL
        azure_url = f"{SEARCH_SERVICE_ENDPOINT}/indexes/{INDEX_NAME}/docs/search"
        logger.info(f"Azure URL: {azure_url}")
        
        # Forward headers
        headers = {
            "api-key": ADMIN_KEY,
            "Content-Type": "application/json"
        }
        
        # Prepare search body
        search_body = {
            "search": request.search_text,
            "searchFields": request.search_fields,
            "select": request.select
        }
        logger.info(f"Search body: {json.dumps(search_body, indent=2)}")
        
        # Make the request to Azure AI Search
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url=azure_url,
                    params=params,
                    headers=headers,
                    json=search_body
                )
                
                # Log response status and content
                logger.info(f"Azure Search response status: {response.status_code}")
                logger.info(f"Azure Search response headers: {dict(response.headers)}")
                logger.info(f"Azure Search response text: {response.text}")
                
                if response.status_code != 200:
                    error_msg = f"Azure Search error: {response.text}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=response.status_code, detail=error_msg)
                
                try:
                    # Return the response from Azure AI Search
                    search_results = response.json()
                    formatted_response = {
                        "status": "success",
                        "count": len(search_results.get("value", [])),
                        "results": search_results.get("value", [])
                    }
                    logger.info(f"Formatted response: {json.dumps(formatted_response, indent=2)}")
                    return formatted_response
                except json.JSONDecodeError as e:
                    error_msg = f"Failed to parse Azure Search response: {str(e)}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=500, detail=error_msg)
                    
            except httpx.RequestError as e:
                error_msg = f"Failed to make request to Azure Search: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Unexpected error in forward_to_azure: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=str(e))

# Import routes after app creation to avoid circular imports
from app.api.routes import router as api_router
app.include_router(api_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 