import os
import psycopg2
from psycopg2 import sql

DATABASE_URL = os.environ.get('DATABASE_URL')

def check_alembic_version():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if alembic_version table exists
        cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')")
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("alembic_version table does not exist.")
            return
        
        # Query the alembic_version table
        cur.execute("SELECT version_num FROM alembic_version")
        version = cur.fetchone()
        
        if version:
            print(f"Current version in alembic_version table: {version[0]}")
        else:
            print("No version found in alembic_version table")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    check_alembic_version()
