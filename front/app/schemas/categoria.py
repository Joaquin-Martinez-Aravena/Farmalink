from pydantic import BaseModel

class CategoriaOut(BaseModel):
    id_categoria: int
    nombre: str
    class Config: from_attributes = True