import uuid
from datetime import datetime
from app.db.database import database, users
from app.models.schemas import UserCreate, User
from fastapi import HTTPException

class UserService:
    """
    User management service using repository pattern
    """
    async def create_user(self, user: UserCreate) -> User:
        """
        Create a new user
        """
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        query = users.insert().values(
            id=user_id,
            username=user.username,
            email=user.email,
            created_at=created_at
        )
        
        try:
            await database.execute(query)
            return User(
                id=user_id,
                username=user.username,
                email=user.email,
                created_at=created_at
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def get_user(self, user_id: str) -> User:
        """
        Get a user by ID
        """
        query = users.select().where(users.c.id == user_id)
        user = await database.fetch_one(query)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return User(**dict(user))
    
    async def user_exists(self, user_id: str) -> bool:
        """
        Check if a user exists
        """
        query = users.select().where(users.c.id == user_id)
        user = await database.fetch_one(query)
        return user is not None 