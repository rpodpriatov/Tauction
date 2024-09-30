from sqlalchemy import create_engine, MetaData, inspect
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

inspector = inspect(engine)

print("Current database schema:")
for table_name in metadata.tables:
    print(f"\nTable: {table_name}")
    for column in inspector.get_columns(table_name):
        print(f"  - {column['name']}: {column['type']}")

print("\nSQLAlchemy models:")
from models import User, Auction

print("\nUser model:")
for column in User.__table__.columns:
    print(f"  - {column.name}: {column.type}")

print("\nAuction model:")
for column in Auction.__table__.columns:
    print(f"  - {column.name}: {column.type}")
