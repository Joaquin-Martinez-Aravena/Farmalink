
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..bd import get_session
from ..models import Producto
from ..schemas.producto import ProductoIn, ProductoOut

r = APIRouter(prefix="/api/productos", tags=["Productos"])

@r.get("/", response_model=list[ProductoOut])
async def listar(search: str | None = None, categoria: int | None = None, estado: str | None = None,
                 db: AsyncSession = Depends(get_session)):
    stmt = select(Producto)
    if search:
        stmt = stmt.where((Producto.nombre.ilike(f"%{search}%")) | (Producto.cod_producto.ilike(f"%{search}%")))
    if categoria: stmt = stmt.where(Producto.id_categoria == categoria)
    if estado: stmt = stmt.where(Producto.estado == estado)
    res = await db.execute(stmt.order_by(Producto.nombre.asc()))
    return res.scalars().all()

@r.post("/", response_model=ProductoOut, status_code=201)
async def crear(data: ProductoIn, db: AsyncSession = Depends(get_session)):
    obj = Producto(**data.model_dump())
    db.add(obj); await db.commit(); await db.refresh(obj)
    return obj

@r.put("/{id_producto}", response_model=ProductoOut)
async def actualizar(id_producto: int, data: ProductoIn, db: AsyncSession = Depends(get_session)):
    obj = await db.get(Producto, id_producto)
    if not obj: raise HTTPException(404, "Producto no encontrado")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(obj, k, v)
    await db.commit(); await db.refresh(obj)
    return obj

@r.delete("/{id_producto}")
async def borrar(id_producto: int, db: AsyncSession = Depends(get_session)):
    obj = await db.get(Producto, id_producto)
    if not obj: raise HTTPException(404, "Producto no encontrado")
    await db.delete(obj); await db.commit()
    return {"ok": True}
