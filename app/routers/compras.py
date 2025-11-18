# app/routers/compras.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # Usamos Session normal
from datetime import date

from ..bd import get_db
from ..models import Compra, DetalleCompra, Lote, Proveedor, Producto
from ..schemas.compra import CompraIn, CompraOut
from ..core.email_service import send_purchase_email

router = APIRouter(prefix="/compras", tags=["Compras"])


@router.get("/")
def listar(db: Session = Depends(get_db)):
    rows = db.execute(Compra.__table__.select().order_by(Compra.id_compra.desc()))
    return [dict(r) for r in rows.mappings().all()]


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
    db.flush()  # Para tener compra.id_compra

    # Para usar en el correo
    detalles_email = []

    # Calcular el total y agregar los detalles
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

        # Calcular total
        subtotal = li.cantidad * li.costo_unitario
        total += subtotal

        # Info para el correo
        detalles_email.append(
            {
                "nombre": getattr(producto, "nombre", f"Producto {producto.id_producto}"),
                "cantidad": li.cantidad,
                "costo_unitario": li.costo_unitario,
                "subtotal": subtotal,
                "fecha_venc": li.fecha_venc,
            }
        )

    # Actualizar el total de la compra
    compra.total = total
    db.commit()
    db.refresh(compra)

    # 🚨 Enviar correo directamente (SIN BackgroundTasks) para depurar
    try:
        print("➡️ Antes de llamar a send_purchase_email()")
        send_purchase_email(compra, proveedor, detalles_email)
        print("✅ send_purchase_email() terminó sin excepción")
    except Exception as e:
        print("❌ Error al enviar correo:", repr(e))

    return compra
