
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..bd import get_session
from ..models import Compra, DetalleCompra, Lote, Proveedor, Producto
from ..schemas.compra import CompraIn, CompraOut
from datetime import date

r = APIRouter(prefix="/api/compras", tags=["Compras"])

@r.get("/")
async def listar(db: AsyncSession = Depends(get_session)):
    rows = await db.execute(Compra.__table__.select().order_by(Compra.id_compra.desc()))
    return [dict(r) for r in rows.mappings().all()]

@r.post("/", response_model=CompraOut, status_code=201)
async def crear(payload: CompraIn, db: AsyncSession = Depends(get_session)):
    if not await db.get(Proveedor, payload.id_proveedor):
        raise HTTPException(400, "Proveedor inválido")

    compra = Compra(
        id_proveedor=payload.id_proveedor,
        fecha_compra=date.fromisoformat(payload.fecha_compra),
        total=0,
        id_usuario_registra=payload.id_usuario_registra
    )
    db.add(compra); await db.flush()

    total = 0
    for li in payload.detalle:
        if not await db.get(Producto, li.id_producto):
            raise HTTPException(400, f"Producto inválido: {li.id_producto}")
        db.add(DetalleCompra(
            id_compra=compra.id_compra,
            id_producto=li.id_producto,
            cantidad=li.cantidad,
            costo_unitario=li.costo_unitario
        ))
        db.add(Lote(
            id_compra=compra.id_compra,
            id_producto=li.id_producto,
            fecha_venc=date.fromisoformat(li.fecha_venc),
            stock_lote=li.cantidad
        ))
        total += li.cantidad * li.costo_unitario

    compra.total = total
    await db.commit(); await db.refresh(compra)
    return compra
