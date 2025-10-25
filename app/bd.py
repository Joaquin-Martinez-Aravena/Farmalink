import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Si la URL de la base de datos contiene "ssl=require", la eliminamos
if "ssl=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("ssl=require", "")

# Crear el motor de conexión a la base de datos
engine = create_engine(DATABASE_URL, echo=True)

# Crear una sesión sincrónica
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base
Base = declarative_base()

# Función para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
