
from pydantic import BaseModel
from typing import Optional

class ProveedorIn(BaseModel):
    razon_social: str
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None

class ProveedorOut(ProveedorIn):
    id_proveedor: int
    class Config: from_attributes = True
