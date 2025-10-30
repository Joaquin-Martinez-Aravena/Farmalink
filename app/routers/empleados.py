# app/routers/empleados.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Empleado
from ..schemas.empleado import EmpleadoIn, EmpleadoOut
from ..bd import get_db

r = APIRouter(prefix="/api/empleados", tags=["Empleados"])

@r.get("/", response_model=list[EmpleadoOut])
async def listar_empleados(db: AsyncSession = Depends(get_db)):
    stmt = select(Empleado)
    result = await db.execute(stmt)
    return result.scalars().all()

@r.get("/{id_empleado}", response_model=EmpleadoOut)
async def obtener_empleado(id_empleado: int, db: AsyncSession = Depends(get_db)):
    empleado = await db.get(Empleado, id_empleado)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@r.post("/", response_model=EmpleadoOut, status_code=201)
async def crear_empleado(empleado: EmpleadoIn, db: AsyncSession = Depends(get_db)):
    # Verificar que no exista un empleado con el mismo rut
    existing_empleado = await db.execute(select(Empleado).filter(Empleado.rut == empleado.rut))
    if existing_empleado.scalars().first():
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese RUT")

    # Crear un nuevo empleado
    new_empleado = Empleado(**empleado.dict())
    db.add(new_empleado)
    await db.commit()
    await db.refresh(new_empleado)
    return new_empleado

@r.put("/{id_empleado}", response_model=EmpleadoOut)
async def actualizar_empleado(id_empleado: int, empleado: EmpleadoIn, db: AsyncSession = Depends(get_db)):
    existing_empleado = await db.get(Empleado, id_empleado)
    if not existing_empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    for key, value in empleado.dict().items():
        setattr(existing_empleado, key, value)

    await db.commit()
    await db.refresh(existing_empleado)
    return existing_empleado

@r.delete("/{id_empleado}")
async def borrar_empleado(id_empleado: int, db: AsyncSession = Depends(get_db)):
    empleado = await db.get(Empleado, id_empleado)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    
    await db.delete(empleado)
    await db.commit()
    return {"ok": True}
