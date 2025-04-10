import databases
import sqlalchemy
from sqlalchemy import create_engine
from app.core.config import settings

# Create database connection
database = databases.Database(settings.DATABASE_URL)

# SQLAlchemy setup
metadata = sqlalchemy.MetaData()

# Define tables
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True, index=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
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
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
)

# Create database tables
engine = create_engine(settings.DATABASE_URL)
metadata.create_all(engine) 