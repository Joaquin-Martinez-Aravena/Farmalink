# app/routers/alertas.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..bd import get_db
from ..utils.sql import run_select

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("/stock-bajo")
def stock_bajo(db: Session = Depends(get_db)):
    """
    Obtiene productos con stock bajo según el umbral definido
    
    Returns:
        Lista de productos con stock por debajo del umbral
    """
    return run_select(
        db,
        """
        SELECT * FROM v_stock_producto 
        WHERE estado = 'BAJO' 
        ORDER BY nombre
        """
    )


@router.get("/por-vencer")
def por_vencer(db: Session = Depends(get_db)):
    """
    Obtiene lotes que están por vencer (próximos 30-60 días típicamente)
    
    Returns:
        Lista de lotes próximos a vencer ordenados por fecha
    """
    return run_select(
        db,
        """
        SELECT * FROM v_lotes_por_vencer 
        ORDER BY fecha_venc ASC
        """
    )


@router.get("/vencidos")
def vencidos(db: Session = Depends(get_db)):
    """
    Obtiene lotes que ya están vencidos
    
    Returns:
        Lista de lotes vencidos ordenados por fecha
    """
    return run_select(
        db,
        """
        SELECT * FROM v_lotes_vencidos 
        ORDER BY fecha_venc ASC
        """
    )


@router.get("/resumen")
def resumen_alertas(db: Session = Depends(get_db)):
    """
    Obtiene un resumen de todas las alertas activas
    
    Returns:
        Diccionario con contadores de cada tipo de alerta
    """
    stock_bajo_count = run_select(
        db,
        "SELECT COUNT(*) as total FROM v_stock_producto WHERE estado = 'BAJO'"
    )[0]['total']
    
    por_vencer_count = run_select(
        db,
        "SELECT COUNT(*) as total FROM v_lotes_por_vencer"
    )[0]['total']
    
    vencidos_count = run_select(
        db,
        "SELECT COUNT(*) as total FROM v_lotes_vencidos"
    )[0]['total']
    
    return {
        "stock_bajo": stock_bajo_count,
        "por_vencer": por_vencer_count,
        "vencidos": vencidos_count,
        "total_alertas": stock_bajo_count + por_vencer_count + vencidos_count
    }