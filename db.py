# db.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

# Get the database URL from the config
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create the session factory
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Create the base class for declarative models
Base = declarative_base()
