import uuid
from datetime import datetime
from typing import List, Optional
from app.db.database import database, search_history
from app.models.schemas import SearchHistoryCreate, SearchHistory, SaveSearchRequest
from app.services.user_service import UserService
from fastapi import HTTPException

class HistoryService:
    """
    Search history service using repository pattern
    """
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    async def record_search(self, history: SearchHistoryCreate) -> SearchHistory:
        """
        Record a search in the history
        """
        # Verify user exists
        if not await self.user_service.user_exists(history.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create search history record
        history_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        query = search_history.insert().values(
            id=history_id,
            user_id=history.user_id,
            search_text=history.search_text,
            search_fields=history.search_fields,
            saved=history.saved,
            search_name=history.search_name,
            created_at=created_at
        )
        
        await database.execute(query)
        
        return SearchHistory(
            id=history_id,
            user_id=history.user_id,
            search_text=history.search_text,
            search_fields=history.search_fields,
            saved=history.saved,
            search_name=history.search_name,
            created_at=created_at
        )
    
    async def save_search(self, request: SaveSearchRequest) -> SearchHistory:
        """
        Save a search with a name
        """
        # Verify user exists
        if not await self.user_service.user_exists(request.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verify search history exists
        history_query = search_history.select().where(search_history.c.id == request.search_id)
        history = await database.fetch_one(history_query)
        
        if not history:
            raise HTTPException(status_code=404, detail="Search history not found")
        
        # Update search history
        query = search_history.update().where(
            search_history.c.id == request.search_id
        ).values(
            saved=True,
            search_name=request.search_name
        )
        
        await database.execute(query)
        
        # Get updated record
        updated_query = search_history.select().where(search_history.c.id == request.search_id)
        updated = await database.fetch_one(updated_query)
        
        return SearchHistory(**dict(updated))
    
    async def get_user_search_history(self, user_id: str, saved: Optional[bool] = None) -> List[SearchHistory]:
        """
        Get search history for a user
        """
        # Verify user exists
        if not await self.user_service.user_exists(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build query based on saved parameter
        if saved is not None:
            query = search_history.select().where(
                (search_history.c.user_id == user_id) & (search_history.c.saved == saved)
            )
        else:
            query = search_history.select().where(search_history.c.user_id == user_id)
        
        results = await database.fetch_all(query)
        return [SearchHistory(**dict(result)) for result in results] 