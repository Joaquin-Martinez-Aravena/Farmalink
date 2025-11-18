# app/routers/empleados.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import Empleado
from ..schemas.empleado import EmpleadoIn, EmpleadoOut
from ..bd import get_db

router = APIRouter(prefix="/empleados", tags=["Empleados"])

@router.get("/", response_model=list[EmpleadoOut])
def listar_empleados(db: Session = Depends(get_db)):
    stmt = select(Empleado)
    result = db.execute(stmt)
    return result.scalars().all()

@router.get("/{id_empleado}", response_model=EmpleadoOut)
def obtener_empleado(id_empleado: int, db: Session = Depends(get_db)):
    empleado = db.get(Empleado, id_empleado)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@router.post("/", response_model=EmpleadoOut, status_code=201)
def crear_empleado(empleado: EmpleadoIn, db: Session = Depends(get_db)):
    # Verificar que no exista un empleado con el mismo rut
    existing_empleado = db.execute(select(Empleado).filter(Empleado.rut == empleado.rut))
    if existing_empleado.scalars().first():
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese RUT")

    # Crear un nuevo empleado
    new_empleado = Empleado(**empleado.model_dump())
    db.add(new_empleado)
    db.commit()
    db.refresh(new_empleado)
    return new_empleado

@router.put("/{id_empleado}", response_model=EmpleadoOut)
def actualizar_empleado(id_empleado: int, empleado: EmpleadoIn, db: Session = Depends(get_db)):
    existing_empleado = db.get(Empleado, id_empleado)
    if not existing_empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    for key, value in empleado.model_dump().items():
        setattr(existing_empleado, key, value)

    db.commit()
    db.refresh(existing_empleado)
    return existing_empleado

@router.delete("/{id_empleado}")
def borrar_empleado(id_empleado: int, db: Session = Depends(get_db)):
    empleado = db.get(Empleado, id_empleado)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    db.delete(empleado)
    db.commit()
    return {"ok": True}