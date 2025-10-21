
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..bd import get_session
from ..models import Lote, AjusteLote
from ..schemas.lote import AjusteIn

r = APIRouter(prefix="/api/lotes", tags=["Lotes"])

@r.get("/")
async def listar(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Lote).order_by(Lote.fecha_venc.asc()))
    return res.scalars().all()

@r.post("/{id_lote}/ajustes")
async def ajustar(id_lote: int, data: AjusteIn, db: AsyncSession = Depends(get_session)):
    lot = await db.get(Lote, id_lote)
    if not lot: raise HTTPException(404, "Lote no encontrado")
    nuevo = lot.stock_lote + data.delta
    if nuevo < 0: raise HTTPException(400, "El stock no puede quedar negativo")

    db.add(AjusteLote(id_lote=id_lote, delta=data.delta, motivo=data.motivo, id_usuario=data.id_usuario))
    lot.stock_lote = nuevo
    await db.commit(); await db.refresh(lot)
    return {"ok": True, "stock_lote": lot.stock_lote}
