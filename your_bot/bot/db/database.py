import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from bot.db.base import Base  # твоя декларативная база

# Загружаем DATABASE_URL из .env или напрямую из окружения Docker
DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://news_user:news_password@localhost:5432/news_db")

# Cинхронный движок (для Alembic и фоновых задач)
engine = create_engine(DB_URL, echo=False)

# Сессии для синхронного кода (например, Alembic, RSS-парсеры и рассылки)
Session = sessionmaker(bind=engine)

# 🚀 Необязательно: если хочешь использовать асинхронные сессии
# ASYNC_DB_URL = DB_URL.replace("postgresql+psycopg2", "postgresql+asyncpg")
# async_engine = create_async_engine(ASYNC_DB_URL, echo=False)
# AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# Утилита для создания всех таблиц вручную (если не используешь Alembic)
def init_db():
    Base.metadata.create_all(bind=engine)
