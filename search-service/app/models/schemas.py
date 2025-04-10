from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    search_text: str
    search_fields: Optional[List[str]] = ["hotelName", "description", "category"]
    select: Optional[List[str]] = ["hotelId", "hotelName", "description", "category"]

class SearchResponse(BaseModel):
    status: str
    count: int
    results: List[Dict[str, Any]] 