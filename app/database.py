from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use SQLite for database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./library.db")

# Create an SQLite engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create sessionmaker with AsyncSession
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
async def get_db():
    async with async_session() as session:
        yield session
