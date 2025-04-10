from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SearchRequest(BaseModel):
    search_text: str
    search_fields: Optional[List[str]] = ["hotelName", "description", "category"]
    select: Optional[List[str]] = ["hotelId", "hotelName", "description", "category"]
    user_id: Optional[str] = None

class SaveSearchRequest(BaseModel):
    user_id: str
    search_id: str
    search_name: str

class SearchResponse(BaseModel):
    status: str
    count: int
    results: List[Dict[str, Any]]
    search_id: Optional[str] = None 