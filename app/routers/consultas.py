import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..bd import get_db
from ..utils.sql import run_select, run_exec

router = APIRouter(prefix="/consultas", tags=["Consultas"])

QUERIES_PATH = Path(__file__).resolve().parents[1] / "queries" / "consultas.json"
_catalogo: dict[str, dict] | None = None

def load_catalog():
    global _catalogo
    try:
        with open(QUERIES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        _catalogo = {q["key"]: q for q in data}
        print(f"[CONSULTAS] Catálogo cargado: {len(_catalogo)} consultas")
    except FileNotFoundError:
        print(f"[CONSULTAS] ERROR: Archivo no encontrado: {QUERIES_PATH}")
        _catalogo = {}  # Asegurar que sea un diccionario vacío, no None
    except json.JSONDecodeError as e:
        print(f"[CONSULTAS] ERROR: JSON inválido: {e}")
        _catalogo = {}  # Asegurar que sea un diccionario vacío, no None
    except Exception as e:
        print(f"[CONSULTAS] ERROR inesperado: {e}")
        _catalogo = {}  # Asegurar que sea un diccionario vacío, no None

def get_query(key: str) -> dict:
    if _catalogo is None:
        load_catalog()  # Intentamos cargar el catálogo si no está cargado

    if _catalogo is None:  # Verificamos si después de cargarlo sigue siendo None
        raise HTTPException(status_code=500, detail="Error al cargar el catálogo de consultas.")

    q = _catalogo.get(key)  # Ahora intentamos acceder al catálogo
    if not q:
        raise HTTPException(404, f"Consulta '{key}' no existe")  # Si no se encuentra, lanzamos un error
    return q


@router.get("/", summary="Listar consultas disponibles")  # Changed r to router
def listar():
    if _catalogo is None:  # Verificamos si el catálogo es None
        load_catalog()  # Si lo es, cargamos el catálogo
    if _catalogo is None:  # Aseguramos que el catálogo esté cargado correctamente
        raise HTTPException(status_code=500, detail="Error al cargar el catálogo de consultas.")
    return [{"key": k, "title": v["title"], "type": v["type"], "params": v.get("params", [])}
            for k, v in _catalogo.items()]

class RunIn(BaseModel):
    key: str
    params: dict | None = None

@router.post("/run", summary="Ejecutar consulta por clave")  # Changed r to router
def run(body: RunIn, db: Session = Depends(get_db)):
    q = get_query(body.key)
    safe_params = {k: v for k, v in (body.params or {}).items() if k in q.get("params", [])}

    if q["type"] == "select":
        return run_select(db, q["sql"], **safe_params)
    elif q["type"] == "exec":
        return run_exec(db, q["sql"], **safe_params)
    else:
        raise HTTPException(400, "Tipo de consulta no soportado")

@router.post("/reload", summary="Recargar catálogo (dev)")  # Changed r to router
def reload_catalog():
    load_catalog()
    return {"ok": True, "count": len(_catalogo or {})}