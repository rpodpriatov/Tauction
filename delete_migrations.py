import os

migrations_dir = 'migrations/versions'
if os.path.exists(migrations_dir):
    for filename in os.listdir(migrations_dir):
        if filename != '__init__.py':
            file_path = os.path.join(migrations_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    print(f"Deleted all files in {migrations_dir} except __init__.py")
else:
    print(f"{migrations_dir} does not exist")
