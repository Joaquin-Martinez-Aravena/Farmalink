# app/bd.py
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

load_dotenv()

# Usar SQLite con AioSQLite para operaciones asincrónicas
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./sql/famalink.db")


# Crear engine para la base de datos SQLite asincrónica
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=5,       # Ajusta esto si es necesario
    max_overflow=0,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

Base = declarative_base()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
