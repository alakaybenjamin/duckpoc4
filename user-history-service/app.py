import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import databases
import sqlalchemy
from sqlalchemy import create_engine
from dotenv import load_dotenv

app = FastAPI(title="User & History Service", description="User Management and Search History")

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./user_history.db")
database = databases.Database(DATABASE_URL)

# SQLAlchemy setup
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow),
)

search_history = sqlalchemy.Table(
    "search_history",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.String, sqlalchemy.ForeignKey("users.id")),
    sqlalchemy.Column("search_text", sqlalchemy.String),
    sqlalchemy.Column("search_fields", sqlalchemy.JSON),
    sqlalchemy.Column("saved", sqlalchemy.Boolean, default=False),
    sqlalchemy.Column("search_name", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=datetime.utcnow),
)

# Create database tables
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)

# Models
class UserCreate(BaseModel):
    username: str
    email: str

class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

class SearchHistoryCreate(BaseModel):
    user_id: str
    search_text: str
    search_fields: List[str]
    saved: Optional[bool] = False
    search_name: Optional[str] = None

class SearchHistory(BaseModel):
    id: str
    user_id: str
    search_text: str
    search_fields: List[str]
    saved: bool
    search_name: Optional[str]
    created_at: datetime

class SaveSearchRequest(BaseModel):
    user_id: str
    search_id: str
    search_name: str

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    query = users.insert().values(
        id=user_id,
        username=user.username,
        email=user.email,
        created_at=datetime.utcnow()
    )
    
    try:
        await database.execute(query)
        return {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "created_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return dict(user)

@app.post("/history", response_model=SearchHistory)
async def record_search(history: SearchHistoryCreate):
    # Verify user exists
    user_query = users.select().where(users.c.id == history.user_id)
    user = await database.fetch_one(user_query)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create search history record
    history_id = str(uuid.uuid4())
    query = search_history.insert().values(
        id=history_id,
        user_id=history.user_id,
        search_text=history.search_text,
        search_fields=history.search_fields,
        saved=history.saved,
        search_name=history.search_name,
        created_at=datetime.utcnow()
    )
    
    await database.execute(query)
    
    return {
        "id": history_id,
        "user_id": history.user_id,
        "search_text": history.search_text,
        "search_fields": history.search_fields,
        "saved": history.saved,
        "search_name": history.search_name,
        "created_at": datetime.utcnow()
    }

@app.post("/history/save", response_model=SearchHistory)
async def save_search(request: SaveSearchRequest):
    # Verify user exists
    user_query = users.select().where(users.c.id == request.user_id)
    user = await database.fetch_one(user_query)
    
    if not user:
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
    
    return dict(updated)

@app.get("/history/user/{user_id}", response_model=List[SearchHistory])
async def get_user_search_history(user_id: str, saved: Optional[bool] = None):
    # Verify user exists
    user_query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(user_query)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build query based on saved parameter
    if saved is not None:
        query = search_history.select().where(
            (search_history.c.user_id == user_id) & (search_history.c.saved == saved)
        )
    else:
        query = search_history.select().where(search_history.c.user_id == user_id)
    
    results = await database.fetch_all(query)
    return [dict(result) for result in results]

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5002, reload=True) 