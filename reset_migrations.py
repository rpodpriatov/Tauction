import os
import shutil
from flask_migrate import Migrate, init, migrate, upgrade
from app import app, db_session

# Remove existing migrations
migrations_dir = 'migrations/versions'
if os.path.exists(migrations_dir):
    shutil.rmtree(migrations_dir)
    os.makedirs(migrations_dir)
    print(f"Removed and recreated {migrations_dir}")
else:
    print(f"{migrations_dir} does not exist")

# Initialize Flask-Migrate
migrate = Migrate(app, db_session)

# Create and apply new migration
with app.app_context():
    init()
    migrate(message='initial migration')
    upgrade()

print("Created and applied new initial migration")
