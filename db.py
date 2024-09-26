import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

def get_db_connection(max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            # Verify the connection is still valid
            engine.connect()
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                logging.warning(f"Database connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error(f"Failed to connect to the database after {max_retries} attempts.")
                raise

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=get_db_connection()))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)
