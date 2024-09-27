from db import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('users')
for column in columns:
    print(column['name'], column['type'])