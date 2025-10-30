from fastapi import FastAPI
import os
from .bd_init import run_sql_files  # Asegúrate de tener esta función en bd_init.py
from .routers import empleados, productos, proveedores, compras, lotes, alertas, consultas

# Creación de la aplicación FastAPI
app = FastAPI(title="FarmaLink API", version="0.1.0")

@app.on_event("startup")
def startup_event():
    """Función para inicializar la base de datos al iniciar la aplicación."""
    print("[DB-INIT] Iniciando la base de datos...")
    run_sql_files()  # Esta función debe ser sincrónica ahora

@app.get("/")
def ping():
    return {"ok": True, "name": "FarmaLink API"}

# Incluyendo los routers
app.include_router(empleados.r)
app.include_router(productos.r)
app.include_router(proveedores.r)
app.include_router(compras.r)
app.include_router(lotes.r)
app.include_router(consultas.r)
app.include_router(alertas.r)
