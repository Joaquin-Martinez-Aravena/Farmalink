from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..bd import get_db
from ..models import Categoria

router = APIRouter(prefix="/categorias", tags=["Categorías"])

@router.get("/")
def listar(db: Session = Depends(get_db)):
    stmt = select(Categoria)
    res = db.execute(stmt.order_by(Categoria.nombre.asc()))
    return res.scalars().all()