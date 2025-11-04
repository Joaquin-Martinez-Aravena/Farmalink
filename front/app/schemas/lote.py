
from pydantic import BaseModel

class AjusteIn(BaseModel):
    delta: int
    motivo: str
    id_usuario: int | None = None
