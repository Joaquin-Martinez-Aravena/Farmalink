# app/bd_init.py
import os
from pathlib import Path
from sqlalchemy import text
from .bd import engine

# Fallback sin dependencia
def split_sql_statements(raw: str):
    # divide por ';' al final de línea o EOF (no perfecto, pero suficiente si no hay ';' dentro de strings)
    import re
    return [p.strip() for p in re.split(r";\s*(?=\n|$)", raw) if p.strip()]

SQL_DIR = os.getenv("SQL_DIR", "sql")

ORDER = [
    "00_schema.sql",
    "01_seed.sql",
    # "02_consultas.sql",
]

async def _run_file(conn, file_path: Path):
    raw = file_path.read_text(encoding="utf-8")
    for stmt in split_sql_statements(raw):
        await conn.exec_driver_sql(stmt)

async def run_sql_files():
    base = Path(SQL_DIR)
    if not base.exists():
        print(f"[DB-INIT] Carpeta SQL no existe: {base.resolve()}")
        return

    async with engine.begin() as conn:
        for fname in ORDER:
            fp = base / fname
            if not fp.exists():
                print(f"[DB-INIT] Aviso: {fname} no encontrado, salto.")
                continue
            print(f"[DB-INIT] Ejecutando {fname} ...")
            await _run_file(conn, fp)
    print("[DB-INIT] OK: schema/seed aplicados.")
