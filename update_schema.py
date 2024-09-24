from app import app
from models import User
from db import db_session, engine, Base

with app.app_context():
    Base.metadata.create_all(bind=engine)

print("Database schema updated successfully.")
