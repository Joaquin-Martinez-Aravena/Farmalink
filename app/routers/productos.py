from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..bd import get_db  # Cambié get_session por get_db
from ..models import Producto
from ..schemas.producto import ProductoIn, ProductoOut

r = APIRouter(prefix="/api/productos", tags=["Productos"])

@r.get("/", response_model=list[ProductoOut])
def listar(search: str | None = None, categoria: int | None = None, estado: str | None = None,
    db: Session = Depends(get_db)):  
    stmt = select(Producto)
    if search:
        stmt = stmt.where((Producto.nombre.ilike(f"%{search}%")) | (Producto.cod_producto.ilike(f"%{search}%")))
    if categoria:
        stmt = stmt.where(Producto.id_categoria == categoria)
    if estado:
        stmt = stmt.where(Producto.estado == estado)
    res = db.execute(stmt.order_by(Producto.nombre.asc()))
    return res.scalars().all()

@r.post("/", response_model=ProductoOut, status_code=201)
def crear(data: ProductoIn, db: Session = Depends(get_db)):  
    obj = Producto(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@r.put("/{id_producto}", response_model=ProductoOut)
def actualizar(id_producto: int, data: ProductoIn, db: Session = Depends(get_db)): 
    obj = db.get(Producto, id_producto)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@r.delete("/{id_producto}")
def borrar(id_producto: int, db: Session = Depends(get_db)):  
    obj = db.get(Producto, id_producto)
    if not obj:
        raise HTTPException(404, "Producto no encontrado")
    db.delete(obj)
    db.commit()
    return {"ok": True}
