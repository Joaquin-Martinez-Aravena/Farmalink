from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from .bd_init import run_sql_files  # Asegúrate de tener esta función en bd_init.py
from .routers import productos, proveedores, compras, lotes, alertas, consultas

# Añadimos el contexto para ejecutar las inicializaciones de base de datos
@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("RUN_DB_INIT", "true").lower() == "true":
        try:
            await run_sql_files()  # Ejecuta los archivos SQL al iniciar
            print("[DB-INIT] SQL ejecutado correctamente.")
        except Exception as e:
            print(f"[DB-INIT] Aviso: {e}")
    yield

# Creación de la aplicación FastAPI
app = FastAPI(title="FarmaLink API", version="0.1.0", lifespan=lifespan)

@app.get("/")
def ping():
    return {"ok": True, "name": "FarmaLink API"}

# Incluyendo los routers
app.include_router(productos.r)
app.include_router(proveedores.r)
app.include_router(compras.r)
app.include_router(lotes.r)
app.include_router(consultas.r)
app.include_router(alertas.r)
