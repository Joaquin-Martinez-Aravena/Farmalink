
from pydantic import BaseModel, Field
from typing import List, Optional

class LineaCompra(BaseModel):
    id_producto: int
    cantidad: int = Field(gt=0)
    costo_unitario: float = Field(ge=0)
    fecha_venc: str  # YYYY-MM-DD

class CompraIn(BaseModel):
    id_proveedor: int
    fecha_compra: str
    id_usuario_registra: Optional[int] = None
    detalle: List[LineaCompra]

class CompraOut(BaseModel):
    id_compra: int
    total: float
    class Config: from_attributes = True
