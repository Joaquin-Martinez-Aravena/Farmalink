
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from ..bd import get_session
from ..utils.sql import run_select, run_exec

r = APIRouter(prefix="/api/consultas", tags=["Consultas"])

QUERIES_PATH = Path(__file__).resolve().parents[1] / "queries" / "consultas.json"
_catalogo: dict[str, dict] | None = None

def load_catalog():
    global _catalogo
    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    _catalogo = {q["key"]: q for q in data}

def get_query(key: str) -> dict:
    if _catalogo is None:
        load_catalog()
    q = _catalogo.get(key)
    if not q:
        raise HTTPException(404, f"Consulta '{key}' no existe")
    return q

@r.get("/", summary="Listar consultas disponibles")
async def listar():
    if _catalogo is None:
        load_catalog()
    return [{"key": k, "title": v["title"], "type": v["type"], "params": v.get("params", [])}
            for k, v in _catalogo.items()]

class RunIn(BaseModel):
    key: str
    params: dict | None = None

@r.post("/run", summary="Ejecutar consulta por clave")
async def run(body: RunIn, db: AsyncSession = Depends(get_session)):
    q = get_query(body.key)
    safe_params = {k: v for k, v in (body.params or {}).items() if k in q.get("params", [])}

    if q["type"] == "select":
        return await run_select(db, q["sql"], **safe_params)
    elif q["type"] == "exec":
        return await run_exec(db, q["sql"], **safe_params)
    else:
        raise HTTPException(400, "Tipo de consulta no soportado")

@r.post("/reload", summary="Recargar catálogo (dev)")
async def reload_catalog():
    load_catalog()
    return {"ok": True, "count": len(_catalogo or {})}
