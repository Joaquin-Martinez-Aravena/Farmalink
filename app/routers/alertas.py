
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..bd import get_session

r = APIRouter(prefix="/api/alertas", tags=["Alertas"])

@r.get("/stock-bajo")
async def stock_bajo(db: AsyncSession = Depends(get_session)):
    rows = await db.execute("SELECT * FROM v_stock_producto WHERE estado='BAJO' ORDER BY nombre")
    return [dict(r) for r in rows.mappings().all()]

@r.get("/por-vencer")
async def por_vencer(db: AsyncSession = Depends(get_session)):
    rows = await db.execute("SELECT * FROM v_lotes_por_vencer ORDER BY fecha_venc ASC")
    return [dict(r) for r in rows.mappings().all()]

@r.get("/vencidos")
async def vencidos(db: AsyncSession = Depends(get_session)):
    rows = await db.execute("SELECT * FROM v_lotes_vencidos ORDER BY fecha_venc ASC")
    return [dict(r) for r in rows.mappings().all()]
