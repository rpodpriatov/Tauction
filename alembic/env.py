# alembic/env.py

import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Чтение конфигурации из alembic.ini
config = context.config

# Настройка логирования
fileConfig(config.config_file_name)

# Добавление пути к проекту для импорта моделей
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Base  # Убедитесь, что ваш базовый класс объявлен здесь

# Установка target_metadata
target_metadata = Base.metadata

def run_migrations_online():
    # Получение строки подключения из переменной окружения
    connectable = engine_from_config(
        {
            'sqlalchemy.url': os.getenv('DATABASE_URL')
        },
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Включите для сравнения типов столбцов
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()
