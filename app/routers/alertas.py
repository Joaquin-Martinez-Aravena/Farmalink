# app/routers/alertas.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..bd import get_db
from ..utils.sql import run_select
from ..mongodb import crear_alerta  # 🆕 Importar crear_alerta

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("/stock-bajo")
def stock_bajo(db: Session = Depends(get_db)):
    """Obtiene productos con stock bajo"""
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
    """Obtiene lotes por vencer"""
    return run_select(
        db,
        """
        SELECT * FROM v_lotes_por_vencer 
        ORDER BY fecha_venc ASC
        """
    )


@router.get("/vencidos")
def vencidos(db: Session = Depends(get_db)):
    """Obtiene lotes vencidos"""
    return run_select(
        db,
        """
        SELECT * FROM v_lotes_vencidos 
        ORDER BY fecha_venc ASC
        """
    )


@router.get("/resumen")
def resumen_alertas(db: Session = Depends(get_db)):
    """Obtiene un resumen de todas las alertas activas"""
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


# 🆕 ENDPOINT UNIFICADO PARA EL FRONTEND
@router.get("/productos-alerta")
def productos_en_alerta(db: Session = Depends(get_db)):
    """
    Endpoint unificado que retorna TODOS los productos que requieren atención
    y los guarda en MongoDB automáticamente.
    """
    alertas = []
    
    # 1. Stock bajo
    productos_stock_bajo = run_select(
        db,
        """
        SELECT 
            p.id_producto,
            p.nombre,
            c.nombre as categoria,
            vsp.stock_actual,
            p.umbral_stock,
            'stock_bajo' as tipo_alerta
        FROM v_stock_producto vsp
        JOIN producto p ON vsp.id_producto = p.id_producto
        JOIN categoria c ON p.id_categoria = c.id_categoria
        WHERE vsp.estado = 'BAJO'
        ORDER BY p.nombre
        """
    )
    
    if productos_stock_bajo:
        for prod in productos_stock_bajo:
            descripcion = f"Stock bajo: {prod['stock_actual']} unidades (umbral: {prod['umbral_stock']})"
            
            alertas.append({
                "id_producto": prod["id_producto"],
                "nombre": prod["nombre"],
                "categoria": prod["categoria"],
                "estado": "stock_bajo",
                "fecha_vencimiento": None,
                "lote": None,
                "descripcion": descripcion
            })
            
            # 🆕 Guardar en MongoDB
            try:
                crear_alerta(
                    tipo="STOCK_BAJO",
                    prioridad="ALTA",
                    mensaje=f"Stock bajo en {prod['nombre']}",
                    detalles={
                        "producto": prod['nombre'],
                        "id_producto": prod['id_producto'],
                        "categoria": prod['categoria'],
                        "stock_actual": prod['stock_actual'],
                        "umbral": prod['umbral_stock'],
                        "descripcion": descripcion
                    }
                )
            except Exception as e:
                print(f"⚠️ Error al guardar alerta en MongoDB: {e}")
    
    # 2. Por vencer
    lotes_por_vencer = run_select(
        db,
        """
        SELECT 
            p.id_producto,
            p.nombre,
            c.nombre as categoria,
            lpv.fecha_venc,
            lpv.id_lote,
            lpv.stock_lote,
            lpv.dias_para_vencer
        FROM v_lotes_por_vencer lpv
        JOIN producto p ON lpv.id_producto = p.id_producto
        JOIN categoria c ON p.id_categoria = c.id_categoria
        ORDER BY lpv.fecha_venc ASC
        """
    )
    
    if lotes_por_vencer:
        for lote in lotes_por_vencer:
            dias = lote.get("dias_para_vencer", 0)
            descripcion = f"Vence en {dias} días (Stock: {lote['stock_lote']} unidades)"
            
            alertas.append({
                "id_producto": lote["id_producto"],
                "nombre": lote["nombre"],
                "categoria": lote["categoria"],
                "estado": "por_vencer",
                "fecha_vencimiento": str(lote["fecha_venc"]),
                "lote": lote["id_lote"],
                "descripcion": descripcion
            })
            
            # 🆕 Guardar en MongoDB
            try:
                crear_alerta(
                    tipo="VENCIMIENTO",
                    prioridad="MEDIA",
                    mensaje=f"Producto por vencer: {lote['nombre']}",
                    detalles={
                        "producto": lote['nombre'],
                        "lote": str(lote['id_lote']),
                        "categoria": lote['categoria'],
                        "fecha_vencimiento": str(lote['fecha_venc']),
                        "stock": lote['stock_lote'],
                        "descripcion": descripcion
                    }
                )
            except Exception as e:
                print(f"⚠️ Error al guardar alerta en MongoDB: {e}")
    
    # 3. Vencidos
    lotes_vencidos = run_select(
        db,
        """
        SELECT 
            p.id_producto,
            p.nombre,
            c.nombre as categoria,
            lv.fecha_venc,
            lv.id_lote,
            lv.stock_lote,
            lv.dias_vencido
        FROM v_lotes_vencidos lv
        JOIN producto p ON lv.id_producto = p.id_producto
        JOIN categoria c ON p.id_categoria = c.id_categoria
        ORDER BY lv.fecha_venc ASC
        """
    )
    
    if lotes_vencidos:
        for lote in lotes_vencidos:
            dias = lote.get("dias_vencido", 0)
            descripcion = f"Vencido hace {dias} días (Stock: {lote['stock_lote']} unidades)"
            
            alertas.append({
                "id_producto": lote["id_producto"],
                "nombre": lote["nombre"],
                "categoria": lote["categoria"],
                "estado": "vencido",
                "fecha_vencimiento": str(lote["fecha_venc"]),
                "lote": lote["id_lote"],
                "descripcion": descripcion
            })
            
            # 🆕 Guardar en MongoDB
            try:
                crear_alerta(
                    tipo="VENCIMIENTO",
                    prioridad="CRITICA",
                    mensaje=f"Producto VENCIDO: {lote['nombre']}",
                    detalles={
                        "producto": lote['nombre'],
                        "lote": str(lote['id_lote']),
                        "categoria": lote['categoria'],
                        "fecha_vencimiento": str(lote['fecha_venc']),
                        "stock": lote['stock_lote'],
                        "descripcion": descripcion
                    }
                )
            except Exception as e:
                print(f"⚠️ Error al guardar alerta en MongoDB: {e}")
    
    return alertas