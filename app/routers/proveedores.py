
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..bd import get_session
from ..models import Proveedor
from ..schemas.proveedor import ProveedorIn, ProveedorOut

r = APIRouter(prefix="/api/proveedores", tags=["Proveedores"])


@r.get("/", response_model=list[ProveedorOut])
async def listar(db: AsyncSession = Depends(get_session)):
    res = await db.execute(select(Proveedor).order_by(Proveedor.razon_social.asc()))
    return res.scalars().all()


@r.post("/", response_model=ProveedorOut, status_code=201)
async def crear(data: ProveedorIn, db: AsyncSession = Depends(get_session)):
    obj = Proveedor(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@r.put("/{id_proveedor}", response_model=ProveedorOut)
async def actualizar(id_proveedor: int, data: ProveedorIn, db: AsyncSession = Depends(get_session)):
    obj = await db.get(Proveedor, id_proveedor)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@r.delete("/{id_proveedor}")
async def borrar(id_proveedor: int, db: AsyncSession = Depends(get_session)):
    obj = await db.get(Proveedor, id_proveedor)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    await db.delete(obj)
    await db.commit()
    return {"ok": True}
