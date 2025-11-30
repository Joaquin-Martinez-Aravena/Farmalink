# app/routers/alertasmongo.py

from fastapi import APIRouter
from typing import Dict, Any, List, Optional
from ..mongobd import crear_alerta, obtener_logs_alerta

router = APIRouter(prefix="/alertas-mongo", tags=["Alertas Mongo"])


@router.post("/")
def crear_alerta_endpoint(body: Dict[str, Any]):
    """
    Crear una nueva alerta en MongoDB.
    
    Body ejemplo:
    {
        "tipo": "STOCK_BAJO",
        "prioridad": "ALTA",
        "mensaje": "Stock bajo en producto X",
        "detalles": {
            "producto": "Paracetamol",
            "id_producto": 5,
            "stock_actual": 3,
            "categoria": "Analgésicos"
        }
    }
    """
    alerta_id = crear_alerta(
        tipo=body.get("tipo", "INFO"),
        prioridad=body.get("prioridad", "MEDIA"),
        mensaje=body.get("mensaje", "Alerta sin mensaje"),
        detalles=body.get("detalles", {}),
    )
    
    if alerta_id:
        return {
            "success": True,
            "id": alerta_id,
            "message": "Alerta creada exitosamente"
        }
    else:
        return {
            "success": False,
            "message": "Error al crear alerta"
        }


@router.get("/historial")
def listar_historial_alertas(
    limit: int = 50,
    tipo: Optional[str] = None
):
    """
    Devuelve el historial reciente de logs de alertas almacenados en Mongo.
    
    Query params:
    - limit: cantidad máxima de registros (default: 50)
    - tipo: filtrar por tipo (STOCK, VENCIMIENTO, INGRESO_COMPRA, etc.)
    """
    logs = obtener_logs_alerta(limit)
    
    # Filtrar por tipo si se especifica
    if tipo:
        logs = [log for log in logs if log.get("tipo") == tipo]
    
    return {
        "total": len(logs),
        "items": logs
    }


@router.get("/tipos")
def listar_tipos_alertas():
    """Retorna los tipos de alertas disponibles"""
    return {
        "tipos": [
            {"valor": "STOCK", "descripcion": "Alertas de stock bajo"},
            {"valor": "VENCIMIENTO", "descripcion": "Alertas de productos vencidos o por vencer"},
            {"valor": "INGRESO_COMPRA", "descripcion": "Notificaciones de nuevas compras"},
            {"valor": "INFO", "descripcion": "Información general"}
        ]
    }


@router.get("/estadisticas")
def estadisticas_alertas():
    """Retorna estadísticas de las alertas"""
    from ..mongobd import get_database
    
    try:
        db = get_database()
        
        # Contar por tipo
        pipeline = [
            {
                "$group": {
                    "_id": "$tipo",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        resultado = list(db.logs_alertas.aggregate(pipeline))
        
        stats = {item["_id"]: item["count"] for item in resultado}
        
        return {
            "total_alertas": sum(stats.values()),
            "por_tipo": stats
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "total_alertas": 0,
            "por_tipo": {}
        }