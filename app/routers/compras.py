# app/routers/compras.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from ..bd import get_db
from ..models import Compra, DetalleCompra, Lote, Proveedor, Producto
from ..schemas.compra import CompraIn, CompraOut
from ..core.email_service import send_purchase_email
from ..mongodb import registrar_auditoria, crear_alerta  # 🆕 Importar funciones correctas

router = APIRouter(prefix="/compras", tags=["Compras"])


@router.get("/")
def listar(db: Session = Depends(get_db)):
    rows = db.execute(Compra.__table__.select().order_by(Compra.id_compra.desc()))
    return [dict(r) for r in rows.mappings().all()]


@router.get("/{id_compra}")
def obtener_una(id_compra: int, db: Session = Depends(get_db)):
    """Obtener una compra específica por ID"""
    compra = db.get(Compra, id_compra)
    if not compra:
        raise HTTPException(404, f"Compra #{id_compra} no encontrada")
    return compra


@router.post("/", response_model=CompraOut, status_code=201)
def crear(
    payload: CompraIn,
    db: Session = Depends(get_db),
):
    # Validación del proveedor
    proveedor = db.get(Proveedor, payload.id_proveedor)
    if not proveedor:
        raise HTTPException(400, "Proveedor inválido")

    # Crear la compra
    compra = Compra(
        id_proveedor=payload.id_proveedor,
        fecha_compra=date.fromisoformat(payload.fecha_compra),
        total=0,
        id_usuario_registra=payload.id_usuario_registra,
    )
    db.add(compra)
    db.flush()

    detalles_email = []
    total = 0
    
    for li in payload.detalle:
        producto = db.get(Producto, li.id_producto)
        if not producto:
            raise HTTPException(400, f"Producto inválido: {li.id_producto}")

        # Guardar detalle de compra
        db.add(
            DetalleCompra(
                id_compra=compra.id_compra,
                id_producto=li.id_producto,
                cantidad=li.cantidad,
                costo_unitario=li.costo_unitario,
            )
        )

        # Agregar lote
        db.add(
            Lote(
                id_compra=compra.id_compra,
                id_producto=li.id_producto,
                fecha_venc=date.fromisoformat(li.fecha_venc),
                stock_lote=li.cantidad,
            )
        )

        subtotal = li.cantidad * li.costo_unitario
        total += subtotal

        detalles_email.append(
            {
                "nombre": getattr(producto, "nombre", f"Producto {producto.id_producto}"),
                "cantidad": li.cantidad,
                "costo_unitario": li.costo_unitario,
                "subtotal": subtotal,
                "fecha_venc": li.fecha_venc,
            }
        )

    compra.total = total
    db.commit()
    db.refresh(compra)

    # 🆕 GUARDAR NOTIFICACIÓN EN MONGODB
    try:
        proveedor_nombre = getattr(proveedor, "nombre", None) or getattr(proveedor, "razon_social", None)
        
        # Registrar auditoría
        registrar_auditoria(
            accion="CREAR_COMPRA",
            tabla_afectada="compra",
            id_registro=compra.id_compra,
            usuario={
                "id_usuario": payload.id_usuario_registra,
                "nombre": "Usuario"
            },
            datos_nuevos={
                "id_compra": compra.id_compra,
                "proveedor": proveedor_nombre,
                "total": float(compra.total),
                "fecha_compra": str(compra.fecha_compra),
                "cantidad_productos": len(payload.detalle)
            }
        )
        
        # Crear alerta de nueva compra
        crear_alerta(
            tipo="INGRESO_COMPRA",
            prioridad="INFO",
            mensaje=f"Nueva compra registrada: #{compra.id_compra}",
            detalles={
                "id_compra": compra.id_compra,
                "proveedor": proveedor_nombre,
                "total": float(compra.total),
                "fecha_compra": str(compra.fecha_compra),
                "cantidad_productos": len(payload.detalle),
                "descripcion": f"Compra de {len(payload.detalle)} productos por ${compra.total:,.0f}"
            }
        )
        
        print(f"✅ Notificación de compra #{compra.id_compra} guardada en MongoDB")
        
    except Exception as e:
        print(f"⚠️ Error al guardar en MongoDB: {e}")
        # No fallar la compra si MongoDB falla

    # Enviar correo
    try:
        print("➡️ Antes de llamar a send_purchase_email()")
        send_purchase_email(compra, proveedor, detalles_email)
        print("✅ send_purchase_email() terminó sin excepción")
    except Exception as e:
        print("❌ Error al enviar correo:", repr(e))

    return compra


@router.delete("/{id_compra}", status_code=200)
def eliminar(id_compra: int, db: Session = Depends(get_db)):
    """Eliminar una compra y sus registros relacionados"""
    print(f"🗑️ Intentando eliminar compra #{id_compra}")
    
    compra = db.get(Compra, id_compra)
    if not compra:
        raise HTTPException(404, f"Compra #{id_compra} no encontrada")
    
    try:
        # 1. Eliminar lotes asociados
        lotes = db.query(Lote).filter(Lote.id_compra == id_compra).all()
        lotes_count = len(lotes)
        for lote in lotes:
            db.delete(lote)
        print(f"   ✓ {lotes_count} lote(s) eliminado(s)")
        
        # 2. Eliminar detalles de compra
        detalles = db.query(DetalleCompra).filter(DetalleCompra.id_compra == id_compra).all()
        detalles_count = len(detalles)
        for detalle in detalles:
            db.delete(detalle)
        print(f"   ✓ {detalles_count} detalle(s) eliminado(s)")
        
        # 3. Eliminar la compra
        total_eliminado = compra.total
        db.delete(compra)
        print(f"   ✓ Compra #{id_compra} eliminada")
        
        # 4. Confirmar cambios
        db.commit()
        
        # 🆕 REGISTRAR ELIMINACIÓN EN MONGODB
        try:
            registrar_auditoria(
                accion="ELIMINAR_COMPRA",
                tabla_afectada="compra",
                id_registro=id_compra,
                usuario={
                    "id_usuario": 1,
                    "nombre": "Usuario"
                },
                datos_anteriores={
                    "id_compra": id_compra,
                    "total": float(total_eliminado),
                    "lotes_eliminados": lotes_count,
                    "detalles_eliminados": detalles_count
                }
            )
            print(f"✅ Auditoría de eliminación guardada en MongoDB")
        except Exception as e:
            print(f"⚠️ Error al guardar auditoría: {e}")
        
        print(f"✅ Compra #{id_compra} eliminada exitosamente")
        
        return {
            "message": f"Compra #{id_compra} eliminada exitosamente",
            "id_compra": id_compra,
            "lotes_eliminados": lotes_count,
            "detalles_eliminados": detalles_count,
            "total_eliminado": total_eliminado
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error al eliminar compra #{id_compra}: {e}")
        raise HTTPException(500, f"Error al eliminar compra: {str(e)}")


@router.get("/debug-env")
def debug_env():
    """Endpoint temporal para verificar variables de entorno"""
    import os
    return {
        "SMTP_USER_exists": bool(os.getenv("SMTP_USER")),
        "SMTP_USER_value": os.getenv("SMTP_USER", "NOT_SET")[:5] + "..." if os.getenv("SMTP_USER") else "NOT_SET",
        "SMTP_PASS_exists": bool(os.getenv("SMTP_PASS")),
        "SMTP_HOST": os.getenv("SMTP_HOST", "NOT_SET"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "NOT_SET"),
        "PURCHASE_NOTIFY_EMAIL": os.getenv("PURCHASE_NOTIFY_EMAIL", "NOT_SET"),
    }