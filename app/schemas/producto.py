
from pydantic import BaseModel
from typing import Optional

class ProductoIn(BaseModel):
    cod_producto: Optional[str] = None
    nombre: str
    id_categoria: int
    umbral_stock: int = 0
    estado: str = "ACT"

class ProductoOut(BaseModel):
    id_producto: int
    cod_producto: Optional[str]
    nombre: str
    id_categoria: int
    umbral_stock: int
    estado: str
    class Config: from_attributes = True
