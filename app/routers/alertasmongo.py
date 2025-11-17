# app/alertasmongo.py
from fastapi import APIRouter
from typing import Dict, Any

from ..mongobd import crear_alerta   # 👈 import relativo, importante

router = APIRouter(
    prefix="/alertas-mongo",         # 👈 para no chocar con tu router alertas.py
    tags=["Alertas Mongo"]
)

@router.post("/")
def crear_alerta_endpoint(body: Dict[str, Any]):
    """
    Crea una alerta desde el frontend.
    El body debería traer: tipo, prioridad, mensaje y detalles.
    """
    alerta_id = crear_alerta(
        tipo=body["tipo"],
        prioridad=body["prioridad"],
        mensaje=body["mensaje"],
        detalles=body.get("detalles", {}),
    )
    return {"id": alerta_id}
