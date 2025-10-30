# app/schemas/empleado.py
from pydantic import BaseModel

class EmpleadoIn(BaseModel):
    nombre: str
    apellido: str
    rut: str
    edad: int
    actividad: str

    class Config:
        orm_mode = True

class EmpleadoOut(EmpleadoIn):
    id_empleado: int