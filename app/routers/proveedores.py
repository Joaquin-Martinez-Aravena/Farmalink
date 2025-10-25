from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..bd import get_db  # Cambié get_session por get_db
from ..models import Proveedor
from ..schemas.proveedor import ProveedorIn, ProveedorOut

r = APIRouter(prefix="/api/proveedores", tags=["Proveedores"])

@r.get("/", response_model=list[ProveedorOut])
def listar(db: Session = Depends(get_db)):  
    res = db.execute(select(Proveedor).order_by(Proveedor.razon_social.asc()))
    return res.scalars().all()

@r.post("/", response_model=ProveedorOut, status_code=201)
def crear(data: ProveedorIn, db: Session = Depends(get_db)): 
    obj = Proveedor(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@r.put("/{id_proveedor}", response_model=ProveedorOut)
def actualizar(id_proveedor: int, data: ProveedorIn, db: Session = Depends(get_db)):  
    obj = db.get(Proveedor, id_proveedor)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj

@r.delete("/{id_proveedor}")
def borrar(id_proveedor: int, db: Session = Depends(get_db)):  
    obj = db.get(Proveedor, id_proveedor)
    if not obj:
        raise HTTPException(404, "Proveedor no encontrado")
    db.delete(obj)
    db.commit()
    return {"ok": True}
