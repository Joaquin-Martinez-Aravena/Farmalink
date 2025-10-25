import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Conexión a PostgreSQL con SSL - CORREGIDO
if DATABASE_URL and "sslmode=" not in DATABASE_URL:
    sep = "&" if "?" in DATABASE_URL else "?"
    DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"

# Motor sincrónico para PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Para ver las consultas SQL en consola (opcional)
    pool_size=5,
    max_overflow=0,
)

# Crear la sesión
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependencia para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()