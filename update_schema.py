from models import User, Subscriber  # Import your models
from db import engine, Base  # Import your database engine and Base

def update_schema():
    # Reflect database schema changes to the Base metadata
    Base.metadata.create_all(bind=engine)
    print("Database schema updated successfully.")

if __name__ == "__main__":
    update_schema()