import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de Render - FÓRZALA directamente para probar
DATABASE_URL = "postgresql://farmalink_user:fGCNf8y4Ew28ftBAm8qn6dyql4TnmKxF@dpg-d3u4m73e5dus739d6dng-a.oregon-postgres.render.com/farmalink"

# Si prefieres usar variable de entorno, pero con fallback
# DATABASE_URL = os.environ.get('DATABASE_URL', "postgresql://farmalink_user:fGCNf8y4Ew28ftBAm8qn6dyql4TnmKxF@dpg-d3u4m73e5dus739d6dng-a.oregon-postgres.render.com/farmalink")

print(f"Conectando a: {DATABASE_URL}")  # Para debug

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()