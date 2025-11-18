from fastapi import APIRouter
from typing import Dict, Any
from ..mongobd import crear_alerta, obtener_logs_alerta

router = APIRouter(prefix="/alertas-mongo", tags=["Alertas Mongo"])

@router.post("/")
def crear_alerta_endpoint(body: Dict[str, Any]):
    alerta_id = crear_alerta(
        tipo=body["tipo"],
        prioridad=body["prioridad"],
        mensaje=body["mensaje"],
        detalles=body.get("detalles", {}),
    )
    return {"id": alerta_id}


@router.get("/historial")
def listar_historial_alertas(limit: int = 50):
    """
    Devuelve el historial reciente de logs de alertas almacenados en Mongo.
    """
    logs = obtener_logs_alerta(limit)
    return {"total": len(logs), "items": logs}
