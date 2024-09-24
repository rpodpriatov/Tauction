from app import app
from models import User, Auction
from db import db_session, engine, Base

def update_schema():
    with app.app_context():
        Base.metadata.create_all(bind=engine)
    print("Database schema updated successfully.")

if __name__ == "__main__":
    update_schema()
