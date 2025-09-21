
# app/main.py
from fastapi import FastAPI
from .routers import productos, proveedores, compras, lotes, alertas
from .routers import consultas


app = FastAPI(title="FarmaLink API", version="0.1.0")

@app.get("/")
def ping():
    return {"ok": True, "name": "FarmaLink API"}

app.include_router(productos.r)
app.include_router(proveedores.r)
app.include_router(compras.r)
app.include_router(lotes.r)
app.include_router(consultas.r)
app.include_router(alertas.r)

