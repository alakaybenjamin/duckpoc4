from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class SearchHistoryBase(BaseModel):
    user_id: str
    search_text: str
    search_fields: List[str]
    saved: Optional[bool] = False
    search_name: Optional[str] = None

class SearchHistoryCreate(SearchHistoryBase):
    pass

class SearchHistory(SearchHistoryBase):
    id: str
    created_at: datetime

    class Config:
        orm_mode = True

class SaveSearchRequest(BaseModel):
    user_id: str
    search_id: str
    search_name: str 