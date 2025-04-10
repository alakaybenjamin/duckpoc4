from typing import List, Dict, Optional
from .interfaces import ServiceInterface

class UserHistoryService:
    """
    User & History service client
    """
    def __init__(self, service: ServiceInterface):
        self.service = service
    
    async def record_search(self, user_id: str, search_text: str, search_fields: List[str]) -> Dict:
        """
        Record a search in history
        """
        data = {
            "user_id": user_id,
            "search_text": search_text,
            "search_fields": search_fields,
            "saved": False
        }
        
        return await self.service.call_service("/api/history", "POST", data)
    
    async def save_search(self, user_id: str, search_id: str, search_name: str) -> Dict:
        """
        Save a search with a name
        """
        data = {
            "user_id": user_id,
            "search_id": search_id,
            "search_name": search_name
        }
        
        return await self.service.call_service("/api/history/save", "POST", data)
    
    async def get_user_search_history(self, user_id: str, saved: Optional[bool] = None) -> List[Dict]:
        """
        Get search history for a user
        """
        endpoint = f"/api/history/user/{user_id}"
        if saved is not None:
            endpoint += f"?saved={str(saved).lower()}"
        
        return await self.service.call_service(endpoint, "GET") 