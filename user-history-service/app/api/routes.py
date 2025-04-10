from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.models.schemas import UserCreate, User, SearchHistoryCreate, SearchHistory, SaveSearchRequest
from app.services.user_service import UserService
from app.services.history_service import HistoryService

router = APIRouter(prefix="/api")

# Dependency injection
def get_user_service():
    return UserService()

def get_history_service(user_service: UserService = Depends(get_user_service)):
    return HistoryService(user_service)

# User routes
@router.post("/users", response_model=User)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user)

@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_user(user_id)

# History routes
@router.post("/history", response_model=SearchHistory)
async def record_search(
    history: SearchHistoryCreate,
    history_service: HistoryService = Depends(get_history_service)
):
    return await history_service.record_search(history)

@router.post("/history/save", response_model=SearchHistory)
async def save_search(
    request: SaveSearchRequest,
    history_service: HistoryService = Depends(get_history_service)
):
    return await history_service.save_search(request)

@router.get("/history/user/{user_id}", response_model=List[SearchHistory])
async def get_user_search_history(
    user_id: str,
    saved: Optional[bool] = None,
    history_service: HistoryService = Depends(get_history_service)
):
    return await history_service.get_user_search_history(user_id, saved) 