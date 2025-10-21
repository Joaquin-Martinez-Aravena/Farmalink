import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from .bd import engine

# Cargar las variables de entorno desde .env
load_dotenv()

# Obtener la dirección de los archivos SQL desde el archivo .env
SQL_DIR = os.getenv("SQL_DIR", "farmalink/sql")  # Carpeta que contiene los scripts SQL

# Función para ejecutar los archivos SQL
async def run_sql_files():
    base = Path(SQL_DIR)
    if not base.exists():
        print(f"[DB-INIT] Carpeta SQL no existe: {base.resolve()}")
        return

    # Lista de archivos SQL a ejecutar
    ORDER = [
        "000_database.sql",  # Crea la base de datos
        "001_schema.sql",    # Crea las tablas
        "002_consultas.sql", # Si tienes vistas o stored procedures, los agregas aquí
    ]

    # Ejecutar cada archivo SQL en el orden
    async with engine.begin() as conn:
        for file_name in ORDER:
            file_path = base / file_name
            if not file_path.exists():
                print(f"[DB-INIT] El archivo {file_name} no fue encontrado, salto.")
                continue

            print(f"[DB-INIT] Ejecutando el archivo {file_name}")
            await _run_file(conn, file_path)

# Función auxiliar para ejecutar cada archivo SQL
async def _run_file(conn, file_path: Path):
    # Leer el contenido del archivo SQL
    raw = file_path.read_text(encoding="utf-8")
    # Separar las sentencias SQL
    statements = [s.strip() for s in raw.split(";") if s.strip()]

    # Ejecutar cada sentencia SQL
    for stmt in statements:
        await conn.execute(stmt)

    print(f"[DB-INIT] {file_path.name} ejecutado correctamente.")
