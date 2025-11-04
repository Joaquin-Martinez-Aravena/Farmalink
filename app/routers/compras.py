# app/routers/compras.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session  # Cambiar de AsyncSession a Session
from ..bd import get_db  # Usamos get_db en lugar de get_session
from ..models import Compra, DetalleCompra, Lote, Proveedor, Producto
from ..schemas.compra import CompraIn, CompraOut
from datetime import date

router = APIRouter(prefix="/api/compras", tags=["Compras"])

@router.get("/")
def listar(db: Session = Depends(get_db)):  # Cambiar a Session
    rows = db.execute(Compra.__table__.select().order_by(Compra.id_compra.desc()))  # Eliminar await
    return [dict(r) for r in rows.mappings().all()]

@router.post("/", response_model=CompraOut, status_code=201)
def crear(payload: CompraIn, db: Session = Depends(get_db)):  # Cambiar a Session
    # Validación del proveedor
    if not db.get(Proveedor, payload.id_proveedor):
        raise HTTPException(400, "Proveedor inválido")

    # Crear la compra
    compra = Compra(
        id_proveedor=payload.id_proveedor,
        fecha_compra=date.fromisoformat(payload.fecha_compra),
        total=0,
        id_usuario_registra=payload.id_usuario_registra
    )
    db.add(compra)
    db.flush()  # Confirmar los cambios en la base de datos

    # Calcular el total y agregar los detalles
    total = 0
    for li in payload.detalle:
        if not db.get(Producto, li.id_producto):
            raise HTTPException(400, f"Producto inválido: {li.id_producto}")
        
        db.add(DetalleCompra(
            id_compra=compra.id_compra,
            id_producto=li.id_producto,
            cantidad=li.cantidad,
            costo_unitario=li.costo_unitario
        ))

        # Agregar lote
        db.add(Lote(
            id_compra=compra.id_compra,
            id_producto=li.id_producto,
            fecha_venc=date.fromisoformat(li.fecha_venc),
            stock_lote=li.cantidad
        ))

        # Calcular total
        total += li.cantidad * li.costo_unitario

    # Actualizar el total de la compra
    compra.total = total
    db.commit()  # Confirmar transacción
    db.refresh(compra)  # Refrescar el objeto para obtener los datos actualizados
    return compra
